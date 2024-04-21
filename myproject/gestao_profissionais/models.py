from django.db import models
class Profissional(models.Model):
    coren = models.CharField(max_length=20, primary_key=True)
    nome = models.CharField(max_length=100)
    # Outros campos relevantes para o profissional podem ser adicionados aqui

    def __str__(self):
        return f"{self.nome} ({self.coren})"
# Create your models here.
