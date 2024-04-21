from django.db import models

class Medicamento(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=100)
    apresentacao = models.CharField(max_length=100)
    # Adicione mais campos conforme necessário

    def __str__(self):
        return f"{self.nome} - {self.apresentacao}"
# Create your models here.
