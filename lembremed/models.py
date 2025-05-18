from django.db import models
from django.contrib.auth.models import User

HORA_CHOICES = [(i, f"{i:02d}:00") for i in range(24)]

# Entidades fortes
class Instituicao(models.Model):
	cnpj = models.CharField(max_length=20, primary_key=True)
	usuario = models.OneToOneField(User, on_delete=models.CASCADE)
	nome = models.CharField(max_length=50)
	class Meta:
		permissions = (
			("pode_gerenciar_instituicao", "Pode gerenciar as instituições"),
		)

class Responsavel(models.Model):
	cpf = models.CharField(max_length=14, primary_key=True)
	telegram_id = models.BigIntegerField(null=True)
	hashcode = models.CharField(max_length=40)
	nome = models.CharField(max_length=50)
	email = models.CharField(max_length=80)
	telefone = models.CharField(max_length=20)

class Morador(models.Model):
	cpf = models.CharField(max_length=14, primary_key=True)
	instituicao = models.ForeignKey(Instituicao, on_delete=models.CASCADE)
	nome = models.CharField(max_length=50)
	dt_nascimento = models.DateField()
	responsavel = models.ForeignKey(Responsavel, on_delete=models.CASCADE)
	class Meta:
		permissions = (
			("pode_gerenciar_morador", "Pode gerenciar os moradores"),
			("pode_medicar_morador", "Pode administrar medicamentos nos moradores"),
		)

class SaidaChoices(models.TextChoices):
	TEMPORARIO = 'TP', 'Temporário'
	MUDANCA = 'MD', 'Mudança'
	MORTE = 'MO', 'Morte'

class Saida(models.Model):
	codigo = models.AutoField(primary_key=True)
	morador = models.ForeignKey(Morador, on_delete=models.CASCADE)
	tipo = models.CharField(
		max_length=2,
		choices=SaidaChoices.choices,
		default=SaidaChoices.TEMPORARIO,
	)
	dt_inicio = models.DateField()
	dt_fim = models.DateField(null=True)

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
		unique_together = ('nome', 'instituicao', 'coren')

class Medicamento(models.Model):
	codigo = models.AutoField(primary_key=True)
	principio = models.CharField(max_length=1024)

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
	validade = models.DateField()
	continuo = models.BooleanField(default=True)
	dias_uso = models.IntegerField(null=True, default=0) #Caso o uso nao for continuo, indica por quantos dias usar
	dthr_alteracao = models.DateTimeField(null=True)

	def estimativa_duracao(self): #Duracao estimada em dias
		if (self.qtd_disponivel and self.frequencia and self.apresentacao.razao_prescricao_comercial and self.prescricao):
			return ((self.qtd_disponivel * self.apresentacao.razao_prescricao_comercial) / (self.frequencia * self.prescricao))
		else:
			return 0

class Horario(models.Model):
	codigo = models.AutoField(primary_key=True)
	estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE, related_name='horarios')
	hora = models.IntegerField(choices=HORA_CHOICES)

class Administra(models.Model):
	profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
	morador = models.ForeignKey(Morador, on_delete=models.CASCADE)
	estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE)
	horario = models.ForeignKey(Horario, on_delete=models.CASCADE)
	dthr_administracao = models.DateTimeField(null=True)
	aplicado = models.BooleanField(default=True)

