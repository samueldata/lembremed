from django.test import TestCase
from lembremed.models import Medicamento
from lembremed.models import Apresentacao
from lembremed.views_medicamento import verificar_apresentacoes
from lembremed.utils import popular_tabela_com_csv
from unittest.mock import patch, mock_open

class VerificarApresentacoesTestCase(TestCase):
    def setUp(self):
        # Ensure the database is clean before each test
        Apresentacao.objects.all().delete()

    def test_verificar_apresentacoes(self):
        # Call the function to verify and create presentations
        verificar_apresentacoes()

        # Check if the presentations were created
        apresentacoes = Apresentacao.objects.all()
        self.assertEqual(apresentacoes.count(), 4)

        # Check the details of each presentation
        apresentacao1 = apresentacoes.get(unidade_prescricao='gota(s)')
        self.assertEqual(apresentacao1.unidade_comercial, 'ml(s)')
        self.assertEqual(apresentacao1.razao_prescricao_comercial, 22)

        apresentacao2 = apresentacoes.get(unidade_prescricao='ml(s)')
        self.assertEqual(apresentacao2.unidade_comercial, 'ml(s)')
        self.assertEqual(apresentacao2.razao_prescricao_comercial, 1)

        apresentacao3 = apresentacoes.get(unidade_prescricao='comprimido(s)')
        self.assertEqual(apresentacao3.unidade_comercial, 'comprimido(s)')
        self.assertEqual(apresentacao3.razao_prescricao_comercial, 1)

        apresentacao4 = apresentacoes.get(unidade_prescricao='dose(s)')
        self.assertEqual(apresentacao4.unidade_comercial, 'dose(s)')
        self.assertEqual(apresentacao4.razao_prescricao_comercial, 1)

    def test_verificar_apresentacoes_already_exists(self):
        # Create one presentation manually
        Apresentacao.objects.create(
            unidade_prescricao='gota(s)',
            unidade_comercial='ml(s)',
            razao_prescricao_comercial=22,
        )

        # Call the function to verify and create presentations
        verificar_apresentacoes()

        # Check if the presentations were created
        apresentacoes = Apresentacao.objects.all()
        self.assertEqual(apresentacoes.count(), 4)  # Should still be 4, no duplicates

        # Check the details of each presentation
        apresentacao1 = apresentacoes.get(unidade_prescricao='gota(s)')
        self.assertEqual(apresentacao1.unidade_comercial, 'ml(s)')
        self.assertEqual(apresentacao1.razao_prescricao_comercial, 22)

        apresentacao2 = apresentacoes.get(unidade_prescricao='ml(s)')
        self.assertEqual(apresentacao2.unidade_comercial, 'ml(s)')
        self.assertEqual(apresentacao2.razao_prescricao_comercial, 1)

        apresentacao3 = apresentacoes.get(unidade_prescricao='comprimido(s)')
        self.assertEqual(apresentacao3.unidade_comercial, 'comprimido(s)')
        self.assertEqual(apresentacao3.razao_prescricao_comercial, 1)

        apresentacao4 = apresentacoes.get(unidade_prescricao='dose(s)')
        self.assertEqual(apresentacao4.unidade_comercial, 'dose(s)')
        self.assertEqual(apresentacao4.razao_prescricao_comercial, 1)


class PopularTabelaComCsvTestCase(TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='principio\nParacetamol\nIbuprofeno')
    @patch('lembremed.utils.csv.DictReader')
    def test_popular_tabela_com_csv(self, mock_csv_reader, mock_file):
        # Mock the CSV reader to return specific data
        mock_csv_reader.return_value = [
            {'principio': 'Paracetamol'},
            {'principio': 'Ibuprofeno'}
        ]

        # Call the function to populate the table
        popular_tabela_com_csv()

        # Check if the Medicamento objects were created
        medicamentos = Medicamento.objects.all()
        self.assertEqual(medicamentos.count(), 2)

        medicamento1 = medicamentos.get(principio='Paracetamol')
        self.assertEqual(medicamento1.principio, 'Paracetamol')

        medicamento2 = medicamentos.get(principio='Ibuprofeno')
        self.assertEqual(medicamento2.principio, 'Ibuprofeno')