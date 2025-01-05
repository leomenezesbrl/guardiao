from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import sys


class Operador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    identidade = models.CharField(max_length=20)
    funcao = models.CharField(max_length=100, null=True, blank=True)
    nivel_acesso = models.IntegerField(
        choices=[(1, 'Nível 1'), (2, 'Nível 2'), (3, 'Nível 3')], default=1)

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    identidade = models.CharField(max_length=20)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    foto = models.ImageField(
        upload_to='clientes/fotos/', null=True, blank=True)
    organizacao_militar = models.CharField(
        max_length=100, null=True, blank=True)
    imagem_identidade = models.ImageField(
        upload_to='identidades/', null=True, blank=True)
    isAtivo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Material(models.Model):
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100)
    registro = models.CharField(
        max_length=50, blank=True, null=True, unique=True)
    quantidade_total = models.PositiveIntegerField(default=0)
    quantidade_disponivel = models.PositiveIntegerField(default=0)
    quantidade_emprestada = models.PositiveIntegerField(default=0)

    def atualizar_quantidades(self):
        """
        Atualiza automaticamente as quantidades com base nos empréstimos ativos.
        """
        if self.registro:
            # Materiais com registro único
            emprestado = EmprestimoMaterial.objects.filter(
                material=self,
                emprestimo__isAtiva=True
            ).exists()
            self.quantidade_disponivel = 0 if emprestado else 1
            self.quantidade_emprestada = 1 - self.quantidade_disponivel
        else:
            # Materiais sem registro
            total_emprestado = EmprestimoMaterial.objects.filter(
                material=self,
                emprestimo__isAtiva=True
            ).aggregate(total=Sum('quantidade'))['total'] or 0
            self.quantidade_emprestada = total_emprestado
            self.quantidade_disponivel = self.quantidade_total - total_emprestado

            print("\n===== ATUALIZAÇÃO DE QUANTIDADES =====")
            print(f"Material: {self.nome}")
            print(f"Quantidade Total: {self.quantidade_total}")
            print(f"Quantidade Emprestada: {self.quantidade_emprestada}")
            print(f"Quantidade Disponível: {self.quantidade_disponivel}")

            # Garantir que os valores não sejam negativos
            if self.quantidade_disponivel < 0:
                print("⚠️ Ajustando quantidade disponível para 0.")
                self.quantidade_disponivel = 0
            if self.quantidade_emprestada < 0:
                print("⚠️ Ajustando quantidade emprestada para 0.")
                self.quantidade_emprestada = 0

        self.save(update_fields=[
                  'quantidade_disponivel', 'quantidade_emprestada'])

    def save(self, *args, **kwargs):
        """
        Garante que as quantidades estejam corretas antes de salvar.
        """
        if self.registro:
            self.quantidade_total = 1
            self.quantidade_disponivel = 1 if not EmprestimoMaterial.objects.filter(
                material=self, emprestimo__isAtiva=True).exists() else 0
            self.quantidade_emprestada = 1 - self.quantidade_disponivel
        else:
            self.quantidade_disponivel = self.quantidade_total - self.quantidade_emprestada
            if self.quantidade_disponivel < 0:
                self.quantidade_disponivel = 0

        super().save(*args, **kwargs)

    def __str__(self):
        if self.registro:
            return f"{self.nome} - Registro: {self.registro}"
        return f"{self.nome} (Total: {self.quantidade_total}, Disponível: {self.quantidade_disponivel})"


class StatusEmprestimo(models.TextChoices):
    ATIVADO = 'Ativado', 'Ativado'
    DESATIVADO = 'Desativado', 'Desativado'
    REATIVADO = 'Reativado', 'Reativado'
    CANCELADO = 'Cancelado', 'Cancelado'


class Emprestimo(models.Model):
    isAtiva = models.BooleanField(default=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    operador = models.ForeignKey('Operador', on_delete=models.CASCADE)
    materiais = models.ManyToManyField(
        'Material', through='EmprestimoMaterial')
    destino = models.CharField(max_length=200)
    data_emprestimo = models.DateTimeField(auto_now_add=True)
    data_devolucao = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Atualiza as quantidades dos materiais ao ativar/desativar.
        """
        super().save(*args, **kwargs)
        for item in self.emprestimomaterial_set.all():
            item.material.atualizar_quantidades()

    def __str__(self):
        return f"Empréstimo para {self.cliente.nome}"


# ✅ Pré-exclusão do Empréstimo
@receiver(pre_delete, sender=Emprestimo)
def atualizar_materiais_antes_exclusao(sender, instance, **kwargs):
    print("\n===== INÍCIO DO pre_delete =====")
    sys.stdout.flush()

    for item in instance.emprestimomaterial_set.all():
        material = item.material
        print(f"🛠️ Material: {material.nome}")
        print(f"   Quantidade Emprestada (antes): {
              material.quantidade_emprestada}")
        print(f"   Quantidade Disponível (antes): {
              material.quantidade_disponivel}")
        print(f"   Quantidade Total: {material.quantidade_total}")
        sys.stdout.flush()

        if material.registro:
            # Materiais com registro único
            material.quantidade_disponivel = 1
            material.quantidade_emprestada = 0
        else:
            # Materiais sem registro
            material.quantidade_emprestada -= item.quantidade
            material.quantidade_disponivel += item.quantidade

            # Garantir que os valores não fiquem negativos
            if material.quantidade_emprestada < 0:
                material.quantidade_emprestada = 0
            if material.quantidade_disponivel > material.quantidade_total:
                material.quantidade_disponivel = material.quantidade_total

        print(f"   Quantidade Emprestada (nova): {
              material.quantidade_emprestada}")
        print(f"   Quantidade Disponível (nova): {
              material.quantidade_disponivel}")
        sys.stdout.flush()

        # Salva as mudanças nos materiais
        material.save(
            update_fields=['quantidade_disponivel', 'quantidade_emprestada'])
        print(f"✅ Material '{material.nome}' atualizado com sucesso.")
        sys.stdout.flush()

    print("===== FIM DO pre_delete =====\n")
    sys.stdout.flush()


class EmprestimoHistorico(models.Model):
    emprestimo = models.ForeignKey(
        Emprestimo, on_delete=models.CASCADE, related_name='historico')
    status = models.CharField(max_length=50, choices=StatusEmprestimo.choices)
    data = models.DateTimeField(default=timezone.now)
    operador = models.ForeignKey(
        'Operador', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.emprestimo} - {self.status} em {self.data}"


class EmprestimoMaterial(models.Model):
    emprestimo = models.ForeignKey(Emprestimo, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.material.registro:
            return f"{self.material.nome} - Registro: {self.material.registro} ({self.quantidade} unidade)"
        return f"{self.material.nome} ({self.quantidade} unidades)"


class Case(models.Model):
    descricao = models.CharField(max_length=255)
    responsavel = models.CharField(max_length=100)
    lacre = models.CharField(max_length=50, unique=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.descricao} - {self.lacre}"


class Assinante(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class FuncaoAssinante(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class ProntoArmamento(models.Model):
    data = models.DateField(auto_now_add=True)
    numero = models.PositiveIntegerField(unique=True)
    lacre = models.CharField(max_length=50)

    assinante_1 = models.ForeignKey(
        Assinante, related_name='assinante_1', on_delete=models.CASCADE)
    funcao_1 = models.ForeignKey(
        FuncaoAssinante, related_name='funcao_1', on_delete=models.CASCADE)

    assinante_2 = models.ForeignKey(
        Assinante, related_name='assinante_2', on_delete=models.CASCADE)
    funcao_2 = models.ForeignKey(
        FuncaoAssinante, related_name='funcao_2', on_delete=models.CASCADE)

    assinante_3 = models.ForeignKey(
        Assinante, related_name='assinante_3', on_delete=models.CASCADE)
    funcao_3 = models.ForeignKey(
        FuncaoAssinante, related_name='funcao_3', on_delete=models.CASCADE)

    # Novo campo para armazenar diretamente as tabelas HTML
    tabela = models.TextField()

    def __str__(self):
        return f"Pronto #{self.numero} - {self.data}"
