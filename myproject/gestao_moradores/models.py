from django.db import models
class Morador(models.Model):
    cpf = models.CharField(max_length=11, primary_key=True)
    nome = models.CharField(max_length=50)
    dt_nascimento = models.DateField()

    def __str__(self):
        return self.nome
# Create your models here.
