from . import views
from django.urls import path
from .views import (
    # Cautelas
    emprestimos_view, listar_emprestimos, visualizar_emprestimo, buscar_materiais, buscar_clientes, confirmar_exclusao_emprestimo, excluir_emprestimo,

    # Operadores
    cadastrar_operador, listar_operadores, visualizar_operador, editar_operador, excluir_operador,

    # Clientes
    cadastrar_cliente, listar_clientes, visualizar_cliente, editar_cliente,
    excluir_cliente, confirmar_exclusao_cliente, ativar_desativar_cliente,

    # Materiais
    cadastrar_material, listar_materiais, editar_material, excluir_material,

    # Categorias
    cadastrar_categoria, listar_categorias, editar_categoria, excluir_categoria,

    # Cases
    listar_cases, cadastrar_case, editar_case, excluir_case,

    # Pronto do Armamento
    pronto_armamento, gerar_pronto, visualizar_pronto, excluir_pronto,
    listar_prontos, listar_prontos_anteriores, listar_prontos_mes, listar_prontos_meses,

    # Assinantes e Funções
    listar_assinantes, cadastrar_assinante, editar_assinante, excluir_assinante,
    listar_funcoes, cadastrar_funcao, editar_funcao, excluir_funcao,

    # Autenticação
    login_view, logout_view,

    # Página Inicial
    pagina_inicial,
)

# URLs relacionados às Cautelas
urlpatterns = [
    path('emprestimos/', emprestimos_view, name='emprestimos'),
    path('listar-emprestimos/', listar_emprestimos, name='listar_emprestimos'),
    path('visualizar-emprestimo/<int:emprestimo_id>/',
         visualizar_emprestimo, name='visualizar_emprestimo'),
    path('buscar-materiais/', buscar_materiais, name='buscar_materiais'),
    path('buscar-clientes/', buscar_clientes, name='buscar_clientes'),
    path('emprestimos/confirmar-exclusao/<int:emprestimo_id>/',
         confirmar_exclusao_emprestimo, name='confirmar_exclusao_emprestimo'),
    path('emprestimos/excluir/<int:emprestimo_id>/',
         excluir_emprestimo, name='excluir_emprestimo'),
]

# URLs relacionados aos Operadores
urlpatterns += [
    path('operadores/cadastrar/', cadastrar_operador, name='cadastrar_operador'),
    path('operadores/', listar_operadores, name='listar_operadores'),
    path('operadores/visualizar/<int:operador_id>/',
         visualizar_operador, name='visualizar_operador'),
    path('operadores/editar/<int:operador_id>/',
         editar_operador, name='editar_operador'),
    path('operadores/excluir/<int:operador_id>/',
         excluir_operador, name='excluir_operador'),
]

# URLs relacionados aos Clientes
urlpatterns += [
    path('clientes/cadastrar/', cadastrar_cliente, name='cadastrar_cliente'),
    path('clientes/', listar_clientes, name='listar_clientes'),
    path('clientes/visualizar/<int:cliente_id>/',
         visualizar_cliente, name='visualizar_cliente'),
    path('clientes/editar/<int:cliente_id>/',
         editar_cliente, name='editar_cliente'),
    path('clientes/excluir/<int:cliente_id>/',
         excluir_cliente, name='excluir_cliente'),
    path('clientes/confirmar-exclusao/<int:cliente_id>/',
         confirmar_exclusao_cliente, name='confirmar_exclusao_cliente'),
    path('clientes/ativar-desativar/<int:cliente_id>/',
         ativar_desativar_cliente, name='ativar_desativar_cliente'),
]

# URLs relacionados aos Materiais
urlpatterns += [
    path('materiais/cadastrar/', cadastrar_material, name='cadastrar_material'),
    path('materiais/', listar_materiais, name='listar_materiais'),
    path('materiais/editar/<int:material_id>/',
         editar_material, name='editar_material'),
    path('materiais/excluir/<int:material_id>/',
         excluir_material, name='excluir_material'),
]

# URLs relacionados às Categorias
urlpatterns += [
    path('categorias/cadastrar/', cadastrar_categoria, name='cadastrar_categoria'),
    path('categorias/', listar_categorias, name='listar_categorias'),
    path('categorias/editar/<int:categoria_id>/',
         editar_categoria, name='editar_categoria'),
    path('categorias/excluir/<int:categoria_id>/',
         excluir_categoria, name='excluir_categoria'),
]

# URLs relacionados aos Cases
urlpatterns += [
    path('cases/', listar_cases, name='listar_cases'),
    path('cases/cadastrar/', cadastrar_case, name='cadastrar_case'),
    path('cases/editar/<int:case_id>/', editar_case, name='editar_case'),
    path('cases/excluir/<int:case_id>/', excluir_case, name='excluir_case'),
]


# URLs relacionadas ao Pronto do Armamento
urlpatterns += [
    path('pronto-armamento/', pronto_armamento, name='pronto_armamento'),
    path('pronto-armamento/gerar/', gerar_pronto, name='gerar_pronto'),
    path('pronto-armamento/visualizar/<int:pronto_id>/',
         visualizar_pronto, name='visualizar_pronto'),
    path('pronto-armamento/excluir/<int:pronto_id>/',
         excluir_pronto, name='excluir_pronto'),
    # Página principal de prontos (Mês Atual)
    path('pronto-armamento/listar/', listar_prontos, name='listar_prontos'),

    # Anos Anteriores
    path('pronto-armamento/anteriores/', listar_prontos_anteriores,
         name='listar_prontos_anteriores'),

    # Meses de um Ano Específico
    path('pronto-armamento/ano/<int:ano>/',
         listar_prontos_meses, name='listar_prontos_meses'),

    # Prontos de um Mês Específico
    path('pronto-armamento/ano/<int:ano>/mes/<int:mes>/',
         listar_prontos_mes, name='listar_prontos_mes'),

]

# URLs relacionados aos Assinantes
urlpatterns += [
    path('assinantes/', listar_assinantes, name='listar_assinantes'),
    path('assinantes/cadastrar/', cadastrar_assinante, name='cadastrar_assinante'),
    path('assinantes/editar/<int:assinante_id>/',
         editar_assinante, name='editar_assinante'),
    path('assinantes/excluir/<int:assinante_id>/',
         excluir_assinante, name='excluir_assinante'),
]

# URLs relacionados às Funções
urlpatterns += [
    path('funcoes/', listar_funcoes, name='listar_funcoes'),
    path('funcoes/cadastrar/', cadastrar_funcao, name='cadastrar_funcao'),
    path('funcoes/editar/<int:funcao_id>/',
         editar_funcao, name='editar_funcao'),
    path('funcoes/excluir/<int:funcao_id>/',
         excluir_funcao, name='excluir_funcao'),
]

# URLs de Autenticação
urlpatterns += [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]

# URL da Página Inicial
urlpatterns += [
    path('', pagina_inicial, name='pagina_inicial'),
]
