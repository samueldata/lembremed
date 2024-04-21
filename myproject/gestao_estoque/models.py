from django.db import models
from controle_medicamentos.models import Medicamento

class Estoque(models.Model):
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    quantidade_minima = models.IntegerField()

    def __str__(self):
        return f"{self.medicamento.nome} - Qtd: {self.quantidade}"
# Create your models here.
