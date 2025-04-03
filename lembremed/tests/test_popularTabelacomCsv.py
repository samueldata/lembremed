from django.test import TestCase
from lembremed.models import Apresentacao
from lembremed.views_medicamento import verificar_apresentacoes

class VerificarApresentacoesTestCase(TestCase):
    def setUp(self):
        """
        Limpa o banco de dados antes de cada teste.
        """
        Apresentacao.objects.all().delete()

    def test_verificar_apresentacoes(self):
        """
        Testa se as apresentações são criadas corretamente.
        """
        verificar_apresentacoes()

        apresentacoes = Apresentacao.objects.all()
        self.assertEqual(apresentacoes.count(), 4, "O número de apresentações criadas está incorreto.")

        # Verifica os detalhes de cada apresentação
        apresentacao1 = Apresentacao.objects.get(unidade_prescricao='gota(s)')
        self.assertEqual(apresentacao1.unidade_comercial, 'ml(s)', "Unidade comercial incorreta para 'gota(s)'.")
        self.assertEqual(apresentacao1.razao_prescricao_comercial, 22, "Razão prescrição/comercial incorreta para 'gota(s)'.")

    def test_verificar_apresentacoes_already_exists(self):
        """
        Testa se apresentações duplicadas não são criadas.
        """
        # Cria uma apresentação existente
        Apresentacao.objects.create(
            unidade_prescricao='gota(s)',
            unidade_comercial='ml(s)',
            razao_prescricao_comercial=22,
        )

        # Executa a função para verificar apresentações
        verificar_apresentacoes()

        # Verifica apresentação
        apresentacoes = Apresentacao.objects.all()
        self.assertEqual(apresentacoes.count(), 1, "O número de apresentações criadas está incorreto.")
        # Verifica os detalhes da apresentação existente
        apresentacao1 = Apresentacao.objects.get(unidade_prescricao='gota(s)')
        self.assertEqual(apresentacao1.unidade_comercial, 'ml(s)', "Unidade comercial incorreta para 'gota(s)'.")
        self.assertEqual(apresentacao1.razao_prescricao_comercial, 22, "Razão prescrição/comercial incorreta para 'gota(s)'.")