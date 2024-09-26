from django.db import models
from django.contrib.auth.models import User

# Entidades fortes
class Instituicao(models.Model):
    cnpj = models.CharField(max_length=20, primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    class Meta:
        permissions = (
            ("pode_gerenciar_instituicao", "Pode gerenciar as instituições"),
        )

class Morador(models.Model):
    cpf = models.CharField(max_length=14, primary_key=True)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    dt_nascimento = models.DateField()
    class Meta:
        permissions = (
            ("pode_gerenciar_morador", "Pode gerenciar os moradores"),
            ("pode_medicar_morador", "Pode administrar medicamentos nos moradores"),
        )

class Profissional(models.Model):
    cpf = models.CharField(max_length=14, primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    coren = models.CharField(max_length=10)  # Alterado de IntegerField para CharField

    class Meta:
        permissions = (
            ("pode_gerenciar_profissional", "Pode gerenciar os profissionais"),
        )

class Medicamento(models.Model):
    codigo = models.AutoField(primary_key=True)
    principio = models.CharField(max_length=255)

    def __str__(self):
        return self.principio
    
class Apresentacao(models.Model):
    codigo = models.AutoField(primary_key=True)
    unidade_prescricao = models.CharField(max_length=100)
    unidade_comercial = models.CharField(max_length=100)
    razao_prescricao_comercial = models.DecimalField(max_digits=6, decimal_places=2, null=True)

class Estoque(models.Model):
    codigo = models.AutoField(primary_key=True)
    morador = models.ForeignKey(Morador, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    apresentacao = models.ForeignKey(Apresentacao, on_delete=models.CASCADE)
    concentracao = models.CharField(max_length=50)
    prescricao = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    qtd_disponivel = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    frequencia = models.IntegerField(default=1)
    horarios = models.CharField(max_length=150)
    
class Administra(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    morador = models.ForeignKey(Morador, on_delete=models.CASCADE)
    estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE)
    dthr_administracao = models.DateTimeField(null=True)
