# ==============================
# 📌 Importações
# ==============================

# Django - Autenticação e Autorização
from calendar import month_name
from django.shortcuts import render
from .models import ProntoArmamento
from django.db.models import Count, Max
from django.db.models.functions import ExtractYear, ExtractMonth
from .models import Emprestimo, EmprestimoMaterial
from django.db.models.functions import Coalesce
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

# Django - HTTP e Redirecionamento
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

# Django - Modelos e Banco de Dados
from django.db.models import F, Q, Count, Sum, ExpressionWrapper, IntegerField

# Django - Utilitários
from django.utils import timezone

# Modelos Personalizados
from .models import (
    ProntoArmamento, Assinante, FuncaoAssinante, Categoria,
    Material, Case, Emprestimo, EmprestimoMaterial,
    Operador, Cliente, EmprestimoHistorico
)

# Decoradores Personalizados
from .decorators import nivel_acesso_minimo

# Outras Bibliotecas
from bs4 import BeautifulSoup
from datetime import date
import json
import locale

# Configuração Local
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'C')  # Locale padrão (fallback)


# ==============================
# 📌 1. Autenticação e Sessão
# ==============================


@login_required
@nivel_acesso_minimo(1)
def pagina_inicial(request):
    return render(request, 'pagina_inicial.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('pagina_inicial')
        messages.error(request, 'Nome de usuário ou senha incorretos.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

# ==============================
# 📌 2. Empréstimos
# ==============================


@login_required
@nivel_acesso_minimo(2)
def emprestimos_view(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        destino = request.POST.get('destino')
        data_devolucao = request.POST.get('data_devolucao')
        materiais_ids = request.POST.getlist('materiais')
        quantidades = request.POST.getlist('quantidades')

        cliente = get_object_or_404(Cliente, id=cliente_id)
        operador = get_object_or_404(Operador, user=request.user)

        with transaction.atomic():  # Garante que tudo ou nada seja salvo
            emprestimo = Emprestimo.objects.create(
                cliente=cliente,
                operador=operador,
                destino=destino,
                data_devolucao=data_devolucao
            )

            try:
                for material_id, quantidade in zip(materiais_ids, quantidades):
                    material = get_object_or_404(Material, id=material_id)
                    quantidade = int(quantidade)

                    # Validação para materiais com registro único
                    if material.registro:
                        if EmprestimoMaterial.objects.filter(
                            material=material, emprestimo__isAtiva=True
                        ).exists():
                            messages.error(
                                request,
                                f"O material '{material.nome}' com registro '{material.registro}' já está emprestado."
                            )
                            raise ValueError("Material com registro único já emprestado.")

                        material.quantidade_disponivel = 0

                    # Validação para materiais sem registro
                    else:
                        if material.quantidade_disponivel < quantidade:
                            messages.error(
                                request,
                                f"O material '{material.nome}' não possui quantidade suficiente disponível."
                            )
                            raise ValueError("Quantidade insuficiente para empréstimo.")

                        material.quantidade_disponivel -= quantidade
                        material.quantidade_emprestada += quantidade

                    material.save()

                    EmprestimoMaterial.objects.create(
                        emprestimo=emprestimo,
                        material=material,
                        quantidade=1 if material.registro else quantidade
                    )

                messages.success(request, 'Empréstimo registrado com sucesso!')
                return redirect('listar_emprestimos')

            except ValueError as e:
                messages.error(request, f"Erro: {e}")
                raise

    # Filtrar apenas materiais disponíveis para empréstimo
    materiais = Material.objects.annotate(
        total_emprestados=Count('emprestimomaterial', filter=Q(
            emprestimomaterial__emprestimo__isAtiva=True))
    ).filter(
        Q(registro__isnull=True, quantidade_disponivel__gt=0) |
        Q(registro__isnull=False, total_emprestados=0)
    )

    # **Filtro para clientes ativos**
    clientes = Cliente.objects.filter(isAtivo=True)

    return render(request, 'emprestimos.html', {
        'materiais': materiais,
        'clientes': clientes,
    })


@login_required
def buscar_materiais(request):
    termo_nome = request.GET.get('nome', '').strip()
    termo_registro = request.GET.get('registro', '').strip()

    materiais = Material.objects.annotate(
        total_emprestados=Count('emprestimomaterial', filter=Q(
            emprestimomaterial__emprestimo__isAtiva=True)),
        quantidade_calculada=ExpressionWrapper(
            F('quantidade_total') - F('quantidade_emprestada'),
            output_field=IntegerField()
        )
    ).filter(
        Q(registro__isnull=True, quantidade_calculada__gt=0) |
        Q(registro__isnull=False, total_emprestados=0)
    )

    if termo_nome:
        materiais = materiais.filter(nome__icontains=termo_nome)
    if termo_registro:
        materiais = materiais.filter(registro__icontains=termo_registro)

    resultados = [
        {
            'id': mat.id,
            'nome': mat.nome,
            'registro': mat.registro if mat.registro else 'N/A',
            'quantidade_disponivel': mat.quantidade_calculada if not mat.registro else 1
        }
        for mat in materiais
    ]

    return JsonResponse(resultados, safe=False)


@login_required
@nivel_acesso_minimo(2)
def buscar_clientes(request):
    termo = request.GET.get('nome', '').strip()

    clientes = Cliente.objects.filter(nome__icontains=termo, isAtivo=True)[:10]
    resultados = [
        {'id': cliente.id, 'nome': cliente.nome}
        for cliente in clientes
    ]
    return JsonResponse(resultados, safe=False)


@login_required
@nivel_acesso_minimo(2)
def listar_emprestimos(request):
    filtro = request.GET.get('filtro', 'todos')
    busca_cliente = request.GET.get('busca_cliente', '')

    emprestimos = Emprestimo.objects.all().order_by('-data_emprestimo')

    if filtro == 'ativas':
        emprestimos = emprestimos.filter(isAtiva=True)
    elif filtro == 'inativas':
        emprestimos = emprestimos.filter(isAtiva=False)

    if busca_cliente:
        emprestimos = emprestimos.filter(
            cliente__nome__icontains=busca_cliente)

    return render(request, 'listar_emprestimos.html', {
        'emprestimos': emprestimos,
        'filtro': filtro,
        'busca_cliente': busca_cliente,
    })


# Visualizar Empréstimo
@login_required
@nivel_acesso_minimo(2)
def visualizar_emprestimo(request, emprestimo_id):
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)
    historico = emprestimo.historico.all()
    materiais = EmprestimoMaterial.objects.filter(emprestimo=emprestimo)

    if request.method == 'POST':
        acao = request.POST.get('acao')
        operador = request.user.operador

        if acao == 'desativar' and emprestimo.isAtiva:
            emprestimo.isAtiva = False
            status = 'Desativado'

        elif acao == 'reativar' and not emprestimo.isAtiva:
            emprestimo.isAtiva = True
            status = 'Reativado'

        elif acao == 'cancelar':
            emprestimo.isAtiva = False
            status = 'Cancelado'

        emprestimo.save()
        for item in materiais:
            item.material.atualizar_quantidades()

        EmprestimoHistorico.objects.create(
            emprestimo=emprestimo,
            status=status,
            operador=operador
        )

        messages.success(request, f'Empréstimo {status.lower()} com sucesso!')
        return redirect('visualizar_emprestimo', emprestimo_id=emprestimo.id)

    return render(request, 'visualizar_emprestimo.html', {
        'emprestimo': emprestimo,
        'historico': historico,
        'materiais': materiais
    })


@login_required
@nivel_acesso_minimo(3)
def confirmar_exclusao_emprestimo(request, emprestimo_id):
    """
    Exibe a página de confirmação antes de excluir um empréstimo.
    """
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)
    materiais = EmprestimoMaterial.objects.filter(emprestimo=emprestimo)

    return render(request, 'confirmar_exclusao_emprestimo.html', {
        'emprestimo': emprestimo,
        'materiais': materiais
    })


@login_required
@nivel_acesso_minimo(3)
def excluir_emprestimo(request, emprestimo_id):
    """
    Exclui um empréstimo e atualiza os materiais relacionados.
    """
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)
    id = emprestimo.id
    if request.method == 'POST':
        emprestimo.delete()
        messages.success(request, f"Cautela #{id} excluída com sucesso!")
        return redirect('listar_emprestimos')

    messages.error(request, "Operação inválida.")
    return redirect('listar_emprestimos')


# ==============================
# 📌 3. Operadores
# ==============================


@login_required
@nivel_acesso_minimo(3)
def cadastrar_operador(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nome = request.POST.get('nome')
        identidade = request.POST.get('identidade')
        funcao = request.POST.get('funcao')
        nivel_acesso = request.POST.get('nivel_acesso')

        # Criar o usuário associado
        user = User.objects.create_user(username=username, password=password)
        user.save()

        # Criar o operador associado
        operador = Operador.objects.create(
            user=user,
            nome=nome,
            identidade=identidade,
            funcao=funcao,
            nivel_acesso=int(nivel_acesso)
        )
        operador.save()

        return redirect('listar_operadores')

    return render(request, 'cadastrar_operador.html')


@login_required
@nivel_acesso_minimo(3)
def listar_operadores(request):
    operadores = Operador.objects.all()
    return render(request, 'listar_operadores.html', {'operadores': operadores})


@login_required
@nivel_acesso_minimo(3)
def visualizar_operador(request, operador_id):
    operador = get_object_or_404(Operador, id=operador_id)
    return render(request, 'visualizar_operador.html', {'operador': operador})


@login_required
@nivel_acesso_minimo(3)
def editar_operador(request, operador_id):
    operador = get_object_or_404(Operador, id=operador_id)

    if request.method == 'POST':
        operador.nome = request.POST.get('nome')
        operador.identidade = request.POST.get('identidade')
        operador.funcao = request.POST.get('funcao')
        operador.nivel_acesso = int(request.POST.get('nivel_acesso'))
        operador.save()

        return redirect('listar_operadores')

    return render(request, 'editar_operador.html', {'operador': operador})


@login_required
@nivel_acesso_minimo(3)
def excluir_operador(request, operador_id):
    operador = get_object_or_404(Operador, id=operador_id)
    operador.user.delete()
    operador.delete()
    return redirect('listar_operadores')

# ==============================
# 📌 4. Clientes
# ==============================


@login_required
@nivel_acesso_minimo(3)
def cadastrar_cliente(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        identidade = request.POST.get('identidade')
        cpf = request.POST.get('cpf')
        organizacao_militar = request.POST.get('organizacao_militar')
        foto = request.FILES.get('foto')
        imagem_identidade = request.FILES.get('imagem_identidade')

        Cliente.objects.create(
            nome=nome,
            identidade=identidade,
            cpf=cpf,
            organizacao_militar=organizacao_militar,
            foto=foto,
            imagem_identidade=imagem_identidade,
            isAtivo=True
        )
        messages.success(request, 'Cliente cadastrado com sucesso!')
        return redirect('listar_clientes')

    return render(request, 'cadastrar_cliente.html')


@login_required
@nivel_acesso_minimo(2)
def listar_clientes(request):
    busca_nome = request.GET.get('busca_nome', '').strip()
    busca_om = request.GET.get('busca_om', '').strip()

    # Inicia com todos os clientes
    clientes = Cliente.objects.all()

    # Aplica os filtros apenas se os parâmetros não estiverem vazios
    if busca_nome:
        clientes = clientes.filter(nome__icontains=busca_nome)
    if busca_om:
        clientes = clientes.filter(organizacao_militar__icontains=busca_om)

    return render(request, 'listar_clientes.html', {
        'clientes': clientes,
        'busca_nome': busca_nome,
        'busca_om': busca_om,
    })


@login_required
@nivel_acesso_minimo(2)
def visualizar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return render(request, 'visualizar_cliente.html', {'cliente': cliente})


@login_required
@nivel_acesso_minimo(3)
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        cliente.nome = request.POST.get('nome')
        cliente.identidade = request.POST.get('identidade')
        cliente.cpf = request.POST.get('cpf')
        cliente.organizacao_militar = request.POST.get('organizacao_militar')
        cliente.isAtivo = 'isAtivo' in request.POST

        if 'foto' in request.FILES:
            cliente.foto = request.FILES['foto']
        if 'imagem_identidade' in request.FILES:
            cliente.imagem_identidade = request.FILES['imagem_identidade']

        cliente.save()
        messages.success(request, 'Cliente editado com sucesso!')
        return redirect('listar_clientes')

    return render(request, 'editar_cliente.html', {'cliente': cliente})


@login_required
@nivel_acesso_minimo(3)
def confirmar_exclusao_cliente(request, cliente_id):
    """
    Página de confirmação para exclusão de um cliente.
    """
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return render(request, 'excluir_cliente.html', {'cliente': cliente})


@login_required
@nivel_acesso_minimo(3)
def excluir_cliente(request, cliente_id):
    """
    Exclui um cliente do sistema.
    """
    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.delete()
    messages.success(request, 'Cliente excluído com sucesso!')
    return redirect('listar_clientes')


@login_required
@nivel_acesso_minimo(3)
def ativar_desativar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.isAtivo = not cliente.isAtivo
    cliente.save()
    return redirect('listar_clientes')

# ==============================
# 📌 5. Materiais
# ==============================


@login_required
@nivel_acesso_minimo(3)
def cadastrar_material(request):
    categorias = Categoria.objects.all()

    if request.method == 'POST':
        nome = request.POST.get('nome')
        categoria_id = request.POST.get('categoria')
        registro = request.POST.get('registro')
        quantidade = request.POST.get('quantidade', 0)

        categoria = get_object_or_404(Categoria, id=categoria_id)

        if registro:  # Material com registro único
            Material.objects.create(
                nome=nome,
                categoria=categoria,
                registro=registro,
                quantidade_total=1,
                quantidade_disponivel=1
            )
        else:  # Material sem registro
            material, created = Material.objects.get_or_create(
                nome=nome,
                categoria=categoria,
                registro=None,
                defaults={
                    'quantidade_total': int(quantidade),
                    'quantidade_disponivel': int(quantidade)
                }
            )
            if not created:
                material.quantidade_total += int(quantidade)
                material.quantidade_disponivel += int(quantidade)
                material.save()

        messages.success(request, 'Material cadastrado com sucesso!')
        return redirect('listar_materiais')

    return render(request, 'cadastrar_material.html', {'categorias': categorias})


@login_required
@nivel_acesso_minimo(2)
def listar_materiais(request):
    categoria_id = request.GET.get('categoria')
    termo_busca = request.GET.get('busca', '')

    categorias = Categoria.objects.all()
    materiais = Material.objects.all()

    # Filtrar por categoria, se selecionada
    if categoria_id:
        materiais = materiais.filter(categoria_id=categoria_id)

    # Filtrar por termo de busca
    if termo_busca:
        materiais = materiais.filter(nome__icontains=termo_busca)

    # Agrupar materiais por categoria
    materiais_por_categoria = {}
    for categoria in categorias:
        materiais_categoria = materiais.filter(categoria=categoria)
        if materiais_categoria.exists():
            materiais_por_categoria[categoria.nome] = materiais_categoria

    return render(request, 'listar_materiais.html', {
        'materiais_por_categoria': materiais_por_categoria,
        'categorias': categorias,
        'categoria_selecionada': categoria_id,
        'termo_busca': termo_busca
    })


@login_required
@nivel_acesso_minimo(3)
def editar_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    categorias = Categoria.objects.all()

    if request.method == 'POST':
        nome = request.POST.get('nome')
        categoria_id = request.POST.get('categoria')
        registro = request.POST.get('registro')
        quantidade = request.POST.get('quantidade', 0)

        categoria = get_object_or_404(Categoria, id=categoria_id)

        # Validar se o registro já existe em outro material
        if registro:
            registro_existente = Material.objects.filter(
                registro=registro
            ).exclude(id=material.id).exists()

            if registro_existente:
                messages.error(
                    request, 'Já existe um material com esse registro.')
                return redirect('editar_material', material_id=material.id)

        # Atualizar os campos básicos
        material.nome = nome
        material.categoria = categoria
        material.registro = registro if registro else None

        if registro:  # Materiais com registro único
            material.quantidade_total = 1
            material.quantidade_disponivel = 1 if not EmprestimoMaterial.objects.filter(
                material=material, emprestimo__isAtiva=True).exists() else 0
            material.quantidade_emprestada = 1 - material.quantidade_disponivel
        else:  # Materiais sem registro
            try:
                quantidade = int(quantidade) if quantidade else 0
            except ValueError:
                quantidade = 0

            diferenca = quantidade - material.quantidade_total
            material.quantidade_total = quantidade
            material.quantidade_disponivel += diferenca

            if material.quantidade_disponivel < 0:
                messages.error(
                    request, 'A quantidade disponível não pode ser negativa.')
                return redirect('editar_material', material_id=material.id)

        material.save()
        messages.success(request, 'Material atualizado com sucesso!')
        return redirect('listar_materiais')

    return render(request, 'editar_material.html', {
        'material': material,
        'categorias': categorias
    })


@login_required
@nivel_acesso_minimo(3)
def excluir_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    material.delete()
    messages.success(request, 'Material excluído com sucesso!')
    return redirect('listar_materiais')


# ==============================
# 📌 6. Pronto do Armamento
# ==============================

@login_required
@nivel_acesso_minimo(1)
def pronto_armamento(request):
    cases = Case.objects.all()
    categorias = Categoria.objects.all()
    categorias_materiais = []

    for categoria in categorias:
        # Obter materiais da categoria
        materiais = Material.objects.filter(categoria=categoria).annotate(
            # Total de registros para itens únicos ou quantidade
            total_existente=Count('id'),
            total_na_reserva=Count('id', filter=~Q(
                emprestimomaterial__emprestimo__isAtiva=True)),
            total_emprestados=Count('id', filter=Q(
                emprestimomaterial__emprestimo__isAtiva=True))
        ).order_by('nome')

        # Organizar destinos
        destinos = {}
        emprestimos = EmprestimoMaterial.objects.filter(
            emprestimo__isAtiva=True,
            material__categoria=categoria
        ).select_related('emprestimo')

        for emprestimo in emprestimos:
            nome_material = emprestimo.material.nome
            destino = emprestimo.emprestimo.destino

            if nome_material not in destinos:
                destinos[nome_material] = {}

            if destino not in destinos[nome_material]:
                destinos[nome_material][destino] = 0

            destinos[nome_material][destino] += emprestimo.quantidade

        # Agregar materiais
        materiais_agregados = {}
        for material in materiais:
            nome = material.nome
            if nome not in materiais_agregados:
                materiais_agregados[nome] = {
                    'nome': nome,
                    'total_existente': 0,
                    'total_na_reserva': 0,
                    'total_emprestados': 0,
                    'destinos': destinos.get(nome, {})
                }

            if material.registro:
                # Materiais com registro único
                materiais_agregados[nome]['total_existente'] += 1
                materiais_agregados[nome]['total_emprestados'] += 1 if EmprestimoMaterial.objects.filter(
                    material=material, emprestimo__isAtiva=True).exists() else 0
                materiais_agregados[nome]['total_na_reserva'] += 0 if EmprestimoMaterial.objects.filter(
                    material=material, emprestimo__isAtiva=True).exists() else 1
            else:
                # Materiais sem registro (com quantidade)
                materiais_agregados[nome]['total_existente'] += material.quantidade_total
                materiais_agregados[nome]['total_na_reserva'] += material.quantidade_disponivel
                materiais_agregados[nome]['total_emprestados'] += material.quantidade_emprestada

        categorias_materiais.append({
            'categoria': categoria.nome,
            'materiais': materiais_agregados.values()
        })

    return render(request, 'pronto_armamento.html', {
        'categorias_materiais': categorias_materiais, 'cases': cases
    })


@login_required
@nivel_acesso_minimo(1)
def listar_prontos(request):
    hoje = timezone.now()
    prontos = ProntoArmamento.objects.filter(
        data__year=hoje.year,
        data__month=hoje.month
    ).order_by('-data')
    return render(request, 'listar_prontos.html', {
        'prontos': prontos,
        'titulo': f'Prontos de {hoje.strftime("%B")} {hoje.year}',
    })


@login_required
@nivel_acesso_minimo(1)
def visualizar_pronto(request, pronto_id):
    pronto = get_object_or_404(ProntoArmamento, id=pronto_id)

    if 'HTTP_REFERER' in request.META:
        voltar_url = request.META['HTTP_REFERER']
    else:
        # Fallback para a página inicial caso não haja referência anterior.
        voltar_url = '/'

    return render(request, 'visualizar_pronto.html', {
        'pronto': pronto,
        'voltar_url': voltar_url,
    })


# Gerar pronto
@login_required
@nivel_acesso_minimo(2)
def gerar_pronto(request):
    if request.method == 'POST':
        # Captura o HTML completo enviado pelo frontend
        html_conteudo = request.POST.get('html_conteudo')

        # Usar BeautifulSoup para extrair a div inteira
        soup = BeautifulSoup(html_conteudo, 'html.parser')
        conteudo_salvo = soup.find(
            id="conteudo_salvo")  # Captura a div pelo ID

        if conteudo_salvo:
            # Converte o conteúdo da div para string HTML
            conteudo_html = str(conteudo_salvo)
        else:
            conteudo_html = ""

        # Garantir número único
        ultimo_numero = ProntoArmamento.objects.aggregate(
            max_numero=Max('numero'))['max_numero']
        numero = (ultimo_numero or 0) + 1

        assinante_1 = get_object_or_404(
            Assinante, id=request.POST.get('assinante_1'))
        funcao_1 = get_object_or_404(
            FuncaoAssinante, id=request.POST.get('funcao_1'))
        assinante_2 = get_object_or_404(
            Assinante, id=request.POST.get('assinante_2'))
        funcao_2 = get_object_or_404(
            FuncaoAssinante, id=request.POST.get('funcao_2'))
        assinante_3 = get_object_or_404(
            Assinante, id=request.POST.get('assinante_3'))
        funcao_3 = get_object_or_404(
            FuncaoAssinante, id=request.POST.get('funcao_3'))
        lacre = request.POST.get('lacre')

        try:
            ProntoArmamento.objects.create(
                numero=numero,
                data=timezone.now(),
                lacre=lacre,
                assinante_1=assinante_1,
                funcao_1=funcao_1,
                assinante_2=assinante_2,
                funcao_2=funcao_2,
                assinante_3=assinante_3,
                funcao_3=funcao_3,
                tabela=conteudo_html,
            )
            messages.success(request, f"Pronto Nº {numero} gerado com sucesso!")
        except IntegrityError:
            messages.error(request, "Erro ao gerar pronto. Tente novamente.")
            return redirect('gerar_pronto')

        return redirect('listar_prontos')

    hoje = timezone.now().strftime('%d de %B de %Y')
    cases = Case.objects.all()
    categorias = Categoria.objects.all()
    assinantes = Assinante.objects.all()
    funcoes = FuncaoAssinante.objects.all()

    categorias_materiais = []
    for categoria in categorias:
        # Obter materiais da categoria
        materiais = Material.objects.filter(categoria=categoria).annotate(
            total_existente=Count('id'),
            total_na_reserva=Count('id', filter=~Q(
                emprestimomaterial__emprestimo__isAtiva=True)),
            total_emprestados=Count('id', filter=Q(
                emprestimomaterial__emprestimo__isAtiva=True))
        ).order_by('nome')

        destinos = {}
        emprestimos = EmprestimoMaterial.objects.filter(
            emprestimo__isAtiva=True,
            material__categoria=categoria
        ).select_related('emprestimo')

        for emprestimo in emprestimos:
            nome_material = emprestimo.material.nome
            destino = emprestimo.emprestimo.destino

            if nome_material not in destinos:
                destinos[nome_material] = {}

            if destino not in destinos[nome_material]:
                destinos[nome_material][destino] = 0

            destinos[nome_material][destino] += emprestimo.quantidade

        materiais_agregados = {}
        for material in materiais:
            nome = material.nome
            if nome not in materiais_agregados:
                materiais_agregados[nome] = {
                    'nome': nome,
                    'total_existente': 0,
                    'total_na_reserva': 0,
                    'total_emprestados': 0,
                    'destinos': destinos.get(nome, {})
                }

            if material.registro:
                materiais_agregados[nome]['total_existente'] += 1
                materiais_agregados[nome]['total_emprestados'] += 1 if EmprestimoMaterial.objects.filter(
                    material=material, emprestimo__isAtiva=True).exists() else 0
                materiais_agregados[nome]['total_na_reserva'] += 0 if EmprestimoMaterial.objects.filter(
                    material=material, emprestimo__isAtiva=True).exists() else 1
            else:
                materiais_agregados[nome]['total_existente'] += material.quantidade_total
                materiais_agregados[nome]['total_na_reserva'] += material.quantidade_disponivel
                materiais_agregados[nome]['total_emprestados'] += material.quantidade_emprestada

        categorias_materiais.append({
            'categoria': categoria.nome,
            'materiais': materiais_agregados.values()
        })

    return render(request, 'gerar_pronto.html', {
        'categorias_materiais': categorias_materiais,
        'cases': cases,
        'hoje': hoje,
        'assinantes': assinantes,
        'funcoes': funcoes,
    })


@login_required
@nivel_acesso_minimo(3)  # Somente nível 3 pode excluir
def excluir_pronto(request, pronto_id):
    pronto = get_object_or_404(ProntoArmamento, id=pronto_id)
    if request.method == 'POST':
        pronto.delete()
        messages.success(request, f"Pronto Nº {pronto.numero} excluído com sucesso!")
        return redirect('listar_prontos')
    return render(request, 'confirmar_exclusao_pronto.html', {'pronto': pronto})


@login_required
@nivel_acesso_minimo(1)
def listar_prontos_anteriores(request):
    anos = (ProntoArmamento.objects
            .annotate(ano=ExtractYear('data'))
            .values('ano')
            .annotate(total=Count('id'))
            .order_by('-ano'))
    return render(request, 'listar_prontos_anteriores.html', {
        'anos': anos,
        'titulo': 'Prontos Anteriores',
    })


@login_required
@nivel_acesso_minimo(1)
def listar_prontos_meses(request, ano):
    meses = (ProntoArmamento.objects
             .filter(data__year=ano)
             .annotate(mes=ExtractMonth('data'))
             .values('mes')
             .annotate(total=Count('id'))
             .order_by('mes'))

    # Adicionar o nome do mês ao resultado
    for mes in meses:
        mes['mes_nome'] = month_name[mes['mes']]

    return render(request, 'listar_prontos_meses.html', {
        'meses': meses,
        'ano': ano,
        'titulo': f'Prontos de {ano}',
    })


@login_required
@nivel_acesso_minimo(1)
def listar_prontos_mes(request, ano, mes):
    prontos = ProntoArmamento.objects.filter(
        data__year=ano,
        data__month=mes
    ).order_by('-data')
    mes_nome = month_name[int(mes)]
    return render(request, 'listar_prontos.html', {
        'prontos': prontos,
        'titulo': f'Prontos de {mes_nome} {ano}',
    })


# ==============================
# 📌 7. Categorias
# ==============================

@login_required
@nivel_acesso_minimo(3)
def cadastrar_categoria(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')

        if Categoria.objects.filter(nome=nome).exists():
            messages.error(request, 'Uma categoria com este nome já existe.')
        else:
            Categoria.objects.create(nome=nome, descricao=descricao)
            messages.success(request, 'Categoria cadastrada com sucesso!')
            return redirect('listar_materiais')

    return render(request, 'cadastrar_categoria.html')


@login_required
@nivel_acesso_minimo(3)
def listar_categorias(request):
    """
    Lista todas as categorias disponíveis.
    """
    categorias = Categoria.objects.all()
    termo_busca = request.GET.get('busca', '')

    if termo_busca:
        categorias = categorias.filter(nome__icontains=termo_busca)

    return render(request, 'listar_categorias.html', {
        'categorias': categorias,
        'termo_busca': termo_busca
    })


@login_required
@nivel_acesso_minimo(3)
def editar_categoria(request, categoria_id):
    """
    Edita uma categoria específica.
    """
    categoria = get_object_or_404(Categoria, id=categoria_id)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')

        if Categoria.objects.filter(nome=nome).exclude(id=categoria.id).exists():
            messages.error(request, 'Já existe uma categoria com esse nome.')
        else:
            categoria.nome = nome
            categoria.descricao = descricao
            categoria.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('listar_categorias')

    return render(request, 'editar_categoria.html', {
        'categoria': categoria
    })


@login_required
@nivel_acesso_minimo(3)
def excluir_categoria(request, categoria_id):
    """
    Exclui uma categoria específica.
    """
    categoria = get_object_or_404(Categoria, id=categoria_id)

    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('listar_categorias')

    return render(request, 'excluir_categoria.html', {
        'categoria': categoria
    })


# ==============================
# 📌 8. Cases
# ==============================

@login_required
@nivel_acesso_minimo(2)
def cadastrar_case(request):
    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        responsavel = request.POST.get('responsavel')
        lacre = request.POST.get('lacre')

        if Case.objects.filter(lacre=lacre).exists():
            messages.error(request, 'Já existe um case com esse lacre.')
        else:
            Case.objects.create(
                descricao=descricao,
                responsavel=responsavel,
                lacre=lacre
            )
            messages.success(request, 'Case cadastrado com sucesso!')
            return redirect('listar_cases')

    return render(request, 'cadastrar_case.html')


@login_required
@nivel_acesso_minimo(2)
def listar_cases(request):
    termo_busca = request.GET.get('busca', '')
    cases = Case.objects.all()

    if termo_busca:
        cases = cases.filter(
            Q(descricao__icontains=termo_busca) |
            Q(responsavel__icontains=termo_busca) |
            Q(lacre__icontains=termo_busca)
        )

    return render(request, 'listar_cases.html', {'cases': cases, 'termo_busca': termo_busca})


@login_required
@nivel_acesso_minimo(2)
def editar_case(request, case_id):
    case = get_object_or_404(Case, id=case_id)

    if request.method == 'POST':
        case.descricao = request.POST.get('descricao')
        case.responsavel = request.POST.get('responsavel')
        case.lacre = request.POST.get('lacre')

        if Case.objects.filter(lacre=case.lacre).exclude(id=case.id).exists():
            messages.error(request, 'Já existe outro case com esse lacre.')
        else:
            case.save()
            messages.success(request, 'Case atualizado com sucesso!')
            return redirect('listar_cases')

    return render(request, 'editar_case.html', {'case': case})


@login_required
@nivel_acesso_minimo(2)
def excluir_case(request, case_id):
    case = get_object_or_404(Case, id=case_id)

    if request.method == 'POST':
        case.delete()
        messages.success(request, 'Case excluído com sucesso!')
        return redirect('listar_cases')

    return render(request, 'excluir_case.html', {'case': case})

# ==============================
# 📌 9. Assinantes e Funções
# ==============================


@login_required
@nivel_acesso_minimo(2)
def listar_assinantes(request):
    assinantes = Assinante.objects.all()
    return render(request, 'listar_assinantes.html', {'assinantes': assinantes})


@login_required
@nivel_acesso_minimo(2)
def cadastrar_assinante(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        Assinante.objects.create(nome=nome)
        messages.success(request, 'Assinante cadastrado com sucesso!')
        return redirect('listar_assinantes')
    return render(request, 'cadastrar_assinante.html')


@login_required
@nivel_acesso_minimo(2)
def editar_assinante(request, assinante_id):
    assinante = get_object_or_404(Assinante, id=assinante_id)
    if request.method == 'POST':
        assinante.nome = request.POST.get('nome')
        assinante.save()
        messages.success(request, 'Assinante editado com sucesso!')
        return redirect('listar_assinantes')
    return render(request, 'editar_assinante.html', {'assinante': assinante})


@login_required
@nivel_acesso_minimo(3)
def excluir_assinante(request, assinante_id):
    assinante = get_object_or_404(Assinante, id=assinante_id)
    assinante.delete()
    messages.success(request, 'Assinante excluído com sucesso!')
    return redirect('listar_assinantes')


@login_required
@nivel_acesso_minimo(2)
def listar_funcoes(request):
    funcoes = FuncaoAssinante.objects.all()
    return render(request, 'listar_funcoes.html', {'funcoes': funcoes})


@login_required
@nivel_acesso_minimo(2)
def cadastrar_funcao(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        FuncaoAssinante.objects.create(nome=nome)
        messages.success(request, 'Função cadastrada com sucesso!')
        return redirect('listar_funcoes')
    return render(request, 'cadastrar_funcao.html')


@login_required
@nivel_acesso_minimo(2)
def editar_funcao(request, funcao_id):
    funcao = get_object_or_404(FuncaoAssinante, id=funcao_id)
    if request.method == 'POST':
        funcao.nome = request.POST.get('nome')
        funcao.save()
        messages.success(request, 'Função editada com sucesso!')
        return redirect('listar_funcoes')
    return render(request, 'editar_funcao.html', {'funcao': funcao})


@login_required
@nivel_acesso_minimo(3)
def excluir_funcao(request, funcao_id):
    funcao = get_object_or_404(FuncaoAssinante, id=funcao_id)
    funcao.delete()
    messages.success(request, 'Função excluída com sucesso!')
    return redirect('listar_funcoes')
