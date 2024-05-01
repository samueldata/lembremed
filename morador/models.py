from django.db import models

# Entidades fortes
class Morador(models.Model):
    cpf = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=50)
    dt_nascimento = models.DateField()

class Instituicao(models.Model):
    cnpj = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=50)
    senha = models.CharField(max_length=50)

class Profissional(models.Model):
    cpf = models.IntegerField(primary_key=True)
    #cnpj_instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    coren = models.IntegerField()
    senha = models.CharField(max_length=50)

class Estoque(models.Model):
    codigo = models.AutoField(primary_key=True)
    cpf_morador = models.ForeignKey(Morador, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=0)
    qtd_minima = models.IntegerField(default=0)
    dose = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    frequencia = models.IntegerField()

class Medicamento(models.Model):
    codigo = models.AutoField(primary_key=True)
    apresentacao = models.CharField(max_length=100)

class NomeComercial(models.Model):
    codigo = models.AutoField(primary_key=True)
    codigo_medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    nome_comercial = models.CharField(max_length=100)

class Substancia(models.Model):
    codigo = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)

# Tabelas relacionais
class Compoe(models.Model):
    codigo_estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE)
    codigo_medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('codigo_estoque', 'codigo_medicamento')

class Possui(models.Model):
    codigo_medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    codigo_substancia = models.ForeignKey(Substancia, on_delete=models.CASCADE)
    miligramagem = models.DecimalField(max_digits=8, decimal_places=2)
    class Meta:
        unique_together = ('codigo_medicamento', 'codigo_substancia')

class Administra(models.Model):
    cpf_profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    cpf_morador = models.ForeignKey(Morador, on_delete=models.CASCADE)
    codigo_medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    dthr_administracao = models.DateTimeField(null=True)
    class Meta:
        unique_together = ('cpf_profissional', 'cpf_morador', 'codigo_medicamento')
