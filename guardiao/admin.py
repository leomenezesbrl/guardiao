from django.contrib import admin
from .models import Operador, Cliente, Material, Emprestimo, EmprestimoMaterial, Categoria, EmprestimoHistorico, Case, Assinante, FuncaoAssinante, ProntoArmamento


@admin.register(Operador)
class OperadorAdmin(admin.ModelAdmin):
    list_display = ('user', 'identidade')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'identidade')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'registro', 'quantidade_total',
                    'quantidade_disponivel', 'quantidade_emprestada')
    list_filter = ('categoria',)
    search_fields = ('nome', 'registro')


# Inline para Materiais no Empréstimo
class EmprestimoMaterialInline(admin.TabularInline):
    model = EmprestimoMaterial
    extra = 1


# Inline para Histórico no Empréstimo
class EmprestimoHistoricoInline(admin.TabularInline):
    model = EmprestimoHistorico
    extra = 1
    readonly_fields = ('status', 'data', 'operador')
    can_delete = False


# Admin para Empréstimos
@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'operador', 'destino',
                    'data_emprestimo', 'data_devolucao', 'isAtiva')
    list_filter = ('isAtiva',)
    search_fields = ('cliente__nome', 'operador__user__username', 'destino')
    inlines = [EmprestimoMaterialInline, EmprestimoHistoricoInline]

    def save_model(self, request, obj, form, change):
        """
        Ao salvar um empréstimo, registra automaticamente no histórico.
        """
        if change:
            status = 'Reativado' if obj.isAtiva else 'Desativado'
        else:
            status = 'Ativado'

        obj.save()
        EmprestimoHistorico.objects.create(
            emprestimo=obj,
            status=status,
            operador=request.user.operador if hasattr(
                request.user, 'operador') else None
        )


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'responsavel', 'lacre',
                    'data_criacao', 'data_atualizacao')
    search_fields = ('descricao', 'responsavel', 'lacre')
    list_filter = ('data_criacao', 'data_atualizacao')
    readonly_fields = ('data_criacao', 'data_atualizacao')

    fieldsets = (
        ('Informações Principais', {
            'fields': ('descricao', 'responsavel', 'lacre')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao')
        }),
    )


@admin.register(Assinante)
class AssinanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)
    list_per_page = 20


@admin.register(FuncaoAssinante)
class FuncaoAssinanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)
    list_per_page = 20


@admin.register(ProntoArmamento)
class ProntoArmamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'numero', 'lacre')
    search_fields = ('numero', 'lacre')
    list_filter = ('data',)
    list_per_page = 20
