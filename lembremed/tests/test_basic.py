from django.test import TestCase
from lembremed.models import Medicamento

class BasicTestCase(TestCase):
    def test_medicamento_creation(self):
        """
        Testa a criação de um objeto Medicamento.
        """
        medicamento = Medicamento.objects.create(
            principio="Paracetamol"
        )
        self.assertEqual(medicamento.principio, "Paracetamol")
        self.assertEqual(str(medicamento), "Paracetamol")  # Testa o método __str__