from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class NivelAcessoMiddleware:
    """
    Middleware para verificar o nível de acesso do operador.
    """
    EXCLUDED_VIEWS = ['login_view', 'logout_view']
    EXCLUDED_PATHS = ['/admin/', '/media/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Se o usuário não estiver autenticado, não faz nada
        if not request.user.is_authenticated:
            return None

        # Ignorar verificações para URLs específicas
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return None

        # Ignorar verificações para views específicas
        view_name = view_func.__name__

        if view_name in self.EXCLUDED_VIEWS:
            return None

        operador = getattr(request.user, 'operador', None)
        if not operador:
            return None

        # 🔒 Nível 1: Acesso restrito
        nivel_1_views = [
            'pronto_armamento',
            'pagina_inicial',
            'listar_prontos',
            'visualizar_pronto',
            'listar_prontos_anteriores',
            'listar_prontos_meses'
        ]
        if operador.nivel_acesso == 1 and view_name not in nivel_1_views:
            messages.error(
                request, "Você não tem permissão para acessar esta página.")
            return redirect('pagina_inicial')

        # 🔒 Nível 2: Acesso intermediário
        nivel_2_views = [
            'emprestimos_view',
            'visualizar_emprestimo',
            'listar_emprestimos',
            'cadastrar_case',
            'editar_case',
            'excluir_case',
            'listar_cases',
            'listar_materiais',
            'listar_clientes',
            'visualizar_cliente',
            'pronto_armamento',
            'pagina_inicial',
            'listar_prontos',
            'visualizar_pronto',
            'gerar_pronto',
            'buscar_clientes',
            'buscar_materiais',
            'listar_prontos_anteriores',
            'listar_prontos_meses'
        ]
        if operador.nivel_acesso == 2 and view_name not in nivel_2_views:
            messages.error(
                request, "Você não tem permissão para acessar esta página.")
            return redirect('pagina_inicial')

        # 🔓 Nível 3: Acesso Total
        return None
