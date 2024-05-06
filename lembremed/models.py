from django.db import models
from django.contrib.auth.models import User

# Entidades fortes
class Morador(models.Model):
    cpf = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=50)
    dt_nascimento = models.DateField()
    class Meta:
        permissions = (
            ("pode_gerenciar_morador", "Pode gerenciar os moradores"),
            ("pode_medicar_morador", "Pode administrar medicamentos nos moradores"),
        )

class Instituicao(models.Model):
    cnpj = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=50)
    senha = models.CharField(max_length=50)

class Profissional(models.Model):
    cpf = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #cnpj_instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    coren = models.IntegerField()
    class Meta:
        permissions = (
            ("pode_gerenciar_profissional", "Pode gerenciar os profissionais"),
        )

class Medicamento(models.Model):
    codigo = models.AutoField(primary_key=True)
    principio = models.CharField(max_length=100)

    def __str__(self):
        return self.principio

class Estoque(models.Model):
    codigo = models.AutoField(primary_key=True)
    morador = models.ForeignKey(Morador, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    tipos_apresentacao = (
        ('comprimido', 'comprimido(s)'),
        ('xarope', 'ml(s)'),
        ('gotas', 'gota(s)'),
        ('dose', 'dose(s)'),
    )
    apresentacao = models.CharField(max_length=10, choices=tipos_apresentacao)
    concentracao = models.CharField(max_length=50)
    prescricao = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    qtd_disponivel = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    frequencia = models.IntegerField(default=1)
    horarios = models.CharField(max_length=150)
    

# Tabelas relacionais
class Administra(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    morador = models.ForeignKey(Morador, on_delete=models.CASCADE)
    estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE)
    dthr_administracao = models.DateTimeField(null=True)
