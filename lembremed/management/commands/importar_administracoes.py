"""
Comando Django para importar dados sintéticos ou históricos de administrações a partir de um arquivo CSV.
Este comando lê um arquivo CSV contendo informações sobre moradores, responsáveis, profissionais, medicamentos,
estoques, horários e registros de administração, vinculando todos os dados à instituição informada pelo CNPJ.
Os dados são inseridos ou atualizados nos respectivos modelos do sistema, garantindo integridade e evitando duplicidades.
Uso:
    python manage.py importar_administracoes <caminho_csv> <cnpj_instituicao>
Exemplo:
    python.manage.py importar_administracoes adm.csv 11.111.111/1111-11
Formato esperado do CSV:
    O arquivo deve conter colunas para os campos principais de cada modelo relacionado à administração de medicamentos,
    como CPF do morador, nome do responsável, dados do profissional, medicamento, apresentação, estoque, horários e
    registros de administração.
Funcionalidades:
    - Cria ou atualiza registros de Responsável, Morador, Profissional, Medicamento, Apresentação, Estoque e Horário.
    - Registra administrações de medicamentos, associando ao profissional, morador, estoque e horário.
    - Todos os dados são vinculados à instituição informada pelo CNPJ.
    - Operação atômica: em caso de erro, nenhuma alteração é salva no banco de dados.
    - Conversão automática de datas, decimais e valores booleanos a partir do CSV.
Atenção:
    - Certifique-se de que o CNPJ informado já exista no banco de dados.
    - O comando pode ser utilizado tanto para importar dados sintéticos (para testes) quanto para restaurar backups históricos.
"""
import csv
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User
from lembremed.models import (
    Instituicao, Responsavel, Morador, Profissional, Medicamento, Apresentacao, Estoque, Horario, Administra
)
from datetime import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = 'Importa dados sintéticos de um CSV, cobrindo todos os modelos principais e campos.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Caminho para o arquivo CSV')
        parser.add_argument('instituicao_cnpj', type=str, help='CNPJ da instituição para vincular os dados')
    
    def normaliza_cpf(self, cpf):
        """Normaliza um CPF removendo caracteres não numéricos"""
        return ''.join(filter(str.isdigit, str(cpf))) if cpf else ''
    
    def pre_processar_profissionais(self, csv_path, instituicao):
        """
        Pré-processa todos os profissionais do CSV e garante sua existência única no banco de dados
        Retorna um dicionário com o CPF normalizado como chave e o objeto Profissional como valor
        """
        profissionais_dict = {}
        
        with open(csv_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cpf_prof = self.normaliza_cpf(row.get('CPF Profissional', ''))
                nome_prof = row.get('Enfermeiro Responsável', '').strip()
                coren_prof = row.get('Coren', '').strip()
                
                if not cpf_prof:
                    self.stdout.write(self.style.WARNING(f"[AVISO] Linha sem CPF de profissional (nome: {nome_prof})"))
                    continue
                
                # Se já temos esse CPF no dicionário temporário, pulamos
                if cpf_prof in profissionais_dict:
                    continue
                    
                # Tentamos buscar o profissional pelo CPF
                profissional = Profissional.objects.filter(cpf=cpf_prof).first()
                
                # Se não encontramos, criamos um novo com usuário associado
                if not profissional:
                    # Busca ou cria o usuário vinculado ao profissional
                    user = User.objects.filter(username=cpf_prof).first()
                    if not user:
                        user = User.objects.create_user(username=cpf_prof)
                    
                    # Cria o profissional
                    profissional = Profissional.objects.create(
                        cpf=cpf_prof,
                        nome=nome_prof or 'Profissional Padrão',
                        instituicao=instituicao,
                        coren=coren_prof or '00000',
                        usuario=user
                    )
                    self.stdout.write(self.style.SUCCESS(f"Profissional criado: {cpf_prof}"))
                else:
                    # Atualiza os dados do profissional existente, se necessário
                    atualizado = False
                    if nome_prof and nome_prof != profissional.nome:
                        profissional.nome = nome_prof
                        atualizado = True
                    if coren_prof and coren_prof != profissional.coren:
                        profissional.coren = coren_prof
                        atualizado = True
                    if profissional.instituicao != instituicao:
                        self.stdout.write(self.style.WARNING(
                            f"[AVISO] Profissional {cpf_prof} vinculado à outra instituição. " +
                            f"Mantendo vínculo com: {profissional.instituicao.nome}"
                        ))
                    
                    if atualizado:
                        profissional.save()
                        self.stdout.write(self.style.SUCCESS(f"Profissional atualizado: {cpf_prof}"))
                
                # Adiciona ao dicionário
                profissionais_dict[cpf_prof] = profissional
        
        return profissionais_dict

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = options['csv_path']
        instituicao_cnpj = options['instituicao_cnpj']
        
        try:
            instituicao = Instituicao.objects.get(cnpj=instituicao_cnpj)
        except Instituicao.DoesNotExist:
            raise CommandError(f'Instituição com cnpj {instituicao_cnpj} não encontrada.')

        # FASE 1: Pré-processamento dos profissionais para garantir unicidade
        self.stdout.write(self.style.NOTICE("FASE 1: Pré-processando profissionais..."))
        profissionais_dict = self.pre_processar_profissionais(csv_path, instituicao)
        self.stdout.write(self.style.SUCCESS(f"Profissionais processados: {len(profissionais_dict)}"))

        # FASE 2: Processamento dos dados principais
        self.stdout.write(self.style.NOTICE("FASE 2: Processando administrações..."))
        contador = 0
        
        with open(csv_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Responsável
                responsavel, _ = Responsavel.objects.get_or_create(
                    cpf=row.get('CPF Responsável', '000.000.000-00'),
                    defaults={
                        'nome': row.get('Nome Responsável', 'Responsável Padrão'),
                        'email': row.get('Email Responsável', ''),
                        'telefone': row.get('Telefone Responsável', ''),
                        'hashcode': row.get('Hashcode Responsável', ''),
                    }
                )
                
                # Morador
                morador, _ = Morador.objects.get_or_create(
                    cpf=row.get('CPF Morador', '000.000.000-00'),
                    defaults={
                        'nome': row.get('Morador', 'Morador Padrão'),
                        'dt_nascimento': self.parse_date(row.get('Data Nascimento Morador', '2000-01-01')),
                        'instituicao': instituicao,
                        'responsavel': responsavel
                    }
                )
                
                # Obter o profissional do dicionário pré-processado
                cpf_prof = self.normaliza_cpf(row.get('CPF Profissional', ''))
                if not cpf_prof or cpf_prof not in profissionais_dict:
                    self.stdout.write(self.style.WARNING(
                        f"[AVISO] Ignorando linha: CPF de profissional inválido ou não encontrado no pré-processamento: {cpf_prof}"
                    ))
                    continue
                
                profissional = profissionais_dict[cpf_prof]
                
                # Medicamento
                medicamento, _ = Medicamento.objects.get_or_create(
                    principio=row.get('Medicamento', 'Medicamento Padrão')
                )
                
                # Apresentacao
                apresentacao, _ = Apresentacao.objects.get_or_create(
                    unidade_prescricao=row.get('Unidade Prescricao', 'mg'),
                    unidade_comercial=row.get('Unidade Comercial', 'comprimido'),
                    razao_prescricao_comercial=self.parse_decimal(row.get('Razao Prescricao Comercial', '1'))
                )
                
                # Estoque
                estoque, _ = Estoque.objects.get_or_create(
                    morador=morador,
                    medicamento=medicamento,
                    apresentacao=apresentacao,
                    defaults={
                        'concentracao': row.get('Concentracao', '10mg'),
                        'prescricao': self.parse_decimal(row.get('Prescricao', '1')),
                        'qtd_disponivel': self.parse_decimal(row.get('Qtd Disponivel', '10')),
                        'frequencia': int(row.get('Frequencia', 1)),
                        'validade': self.parse_date(row.get('Validade', '2030-01-01')),
                        'continuo': self.parse_bool(row.get('Uso Contínuo', 'True')),
                        'dias_uso': int(row.get('Dias Uso', 0)),
                        'dthr_alteracao': self.parse_datetime(row.get('Dthr Alteracao', '2025-01-01 00:00:00')),
                    }
                )
                
                # Horario (opcional, pode haver vários por estoque)
                hora_val = row.get('Hora', None)
                if hora_val is not None:
                    # Suporta tanto inteiro (20) quanto string tipo '20:00:00'
                    try:
                        hora_int = int(str(hora_val).split(':')[0])
                        Horario.objects.get_or_create(
                            estoque=estoque,
                            hora=hora_int
                        )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f"[ERRO] Valor inválido para hora: {hora_val} (linha: {row}) - {e}"
                        ))
                
                # Administra (registro da administração)
                if row.get('Data e Hora Real da Administração'):
                    horario = Horario.objects.filter(estoque=estoque).first()
                    Administra.objects.create(
                        profissional=profissional,
                        morador=morador,
                        estoque=estoque,
                        horario=horario,
                        dthr_administracao=self.parse_datetime(row.get('Data e Hora Real da Administração')),
                        aplicado=self.parse_bool(row.get('Aplicado', 'True'))
                    )
                
                contador += 1
                if contador % 100 == 0:
                    self.stdout.write(f"Processadas {contador} linhas...")

        self.stdout.write(self.style.SUCCESS(f'Importação concluída! {contador} administrações processadas.'))

    def parse_date(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except Exception:
            return None

    def parse_datetime(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except Exception:
            return None

    def parse_decimal(self, value):
        try:
            return Decimal(str(value).replace(',', '.'))
        except Exception:
            return Decimal('0')

    def parse_bool(self, value):
        return str(value).strip().lower() in ['true', '1', 'sim', 'yes']
