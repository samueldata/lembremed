from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User, Permission  # Importação corrigida
from lembremed.models import Medicamento, Apresentacao, Morador, Instituicao, Responsavel
from lembremed.views_medicamento import verificar_apresentacoes
from lembremed.utils import popular_tabela_com_csv
from unittest.mock import patch, mock_open
from datetime import date

class MedicamentoModelTestCase(TestCase):
    def test_medicamento_creation_and_retrieval(self):
        """
        Testa a criação e recuperação de um objeto Medicamento.
        """
        medicamento = Medicamento.objects.create(principio="Ibuprofeno")
        self.assertEqual(Medicamento.objects.count(), 1)
        self.assertEqual(medicamento.principio, "Ibuprofeno")
        self.assertEqual(str(medicamento), "Ibuprofeno")  # Testa o método __str__

class ApresentacaoModelTestCase(TestCase):
    def test_apresentacao_creation(self):
        """
        Testa a criação de um objeto Apresentacao.
        """
        apresentacao = Apresentacao.objects.create(
            unidade_prescricao="comprimido(s)",
            unidade_comercial="caixa(s)",
            razao_prescricao_comercial=10
        )
        self.assertEqual(Apresentacao.objects.count(), 1)
        self.assertEqual(apresentacao.unidade_prescricao, "comprimido(s)")
        self.assertEqual(apresentacao.unidade_comercial, "caixa(s)")
        self.assertEqual(apresentacao.razao_prescricao_comercial, 10)

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Cria um usuário de teste
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Adiciona a permissão necessária ao usuário
        permission = Permission.objects.get(codename='pode_gerenciar_morador')
        self.user.user_permissions.add(permission)

        # Autentica o usuário
        self.client.login(username='testuser', password='testpassword')

        # Cria uma instituição associada ao usuário
        self.instituicao = Instituicao.objects.create(nome="Instituição Teste", usuario=self.user)

        # Cria um responsável para o morador
        self.responsavel = Responsavel.objects.create(
            cpf="12345678901",  # CPF válido
            nome="Responsável Teste", 
        )

        # Cria um morador associado à instituição e ao responsável
        self.morador = Morador.objects.create(
            nome="Morador Teste",
            instituicao=self.instituicao,
            dt_nascimento=date(1990, 1, 1),  # Adiciona uma data de nascimento válida
            responsavel=self.responsavel  # Associa o responsável corretamente
        )

    def test_home_view_status_code(self):
        """
        Testa se a view da página inicial retorna status 200.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_morador_view_status_code(self):
        """
        Testa se a view de 'morador' retorna status 200.
        """
        # Simula o contexto necessário para a view
        session = self.client.session
        session['usuario'] = self.instituicao.cnpj  # Adiciona o ID da instituição à sessão
        session.save()

        response = self.client.get(reverse('morador_listar'))
        self.assertEqual(response.status_code, 200)

class UtilsTestCase(TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='principio\nParacetamol\nIbuprofeno')
    @patch('lembremed.utils.csv.DictReader')
    def test_popular_tabela_com_csv(self, mock_csv_reader, mock_file):
        """
        Testa se a tabela é populada corretamente a partir de um CSV.
        """
        mock_csv_reader.return_value = [
            {'principio': 'Paracetamol'},
            {'principio': 'Ibuprofeno'}
        ]

        popular_tabela_com_csv()

        medicamentos = Medicamento.objects.all()
        self.assertEqual(medicamentos.count(), 2)
        self.assertEqual(medicamentos[0].principio, "Paracetamol")
        self.assertEqual(medicamentos[1].principio, "Ibuprofeno")

class URLTestCase(TestCase):
    def test_home_url_resolves(self):
        """
        Testa se a URL da página inicial resolve para a view correta.
        """
        resolver = resolve('/')
        self.assertEqual(resolver.view_name, 'index')  # Substitua 'home' pela sua view nomeada

    def test_morador_url_resolves(self):
        """
        Testa se a URL de 'morador' resolve para a view correta.
        """
        resolver = resolve('/morador/')
        self.assertEqual(resolver.view_name, 'morador_listar')  # Substitua 'morador' pela sua view nomeada