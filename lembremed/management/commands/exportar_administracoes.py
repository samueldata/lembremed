"""
Comando Django para exportar dados de administrações para um arquivo CSV.
Este comando exporta informações sobre moradores, responsáveis, profissionais, medicamentos,
estoques, horários e registros de administração, seguindo o mesmo formato utilizado para importação.
Uso:
    python manage.py exportar_administracoes <caminho_saida_csv> [<cnpj_instituicao>] [--periodo_inicio YYYY-MM-DD] [--periodo_fim YYYY-MM-DD]
Exemplo:
    python manage.py exportar_administracoes backup_administracoes.csv 11.111.111/1111-11
    python manage.py exportar_administracoes backup_mensal.csv --periodo_inicio 2024-04-01 --periodo_fim 2024-04-30
Funcionalidades:
    - Exporta registros completos relacionados a administrações de medicamentos
    - Filtragem opcional por instituição (CNPJ) e/ou período de data
    - Formato compatível com o comando importar_administracoes
    - Inclui todos os dados necessários para restauração completa
"""
import csv
import os
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from lembremed.models import (
    Instituicao, Responsavel, Morador, Profissional, Medicamento,
    Apresentacao, Estoque, Horario, Administra
)
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Exporta dados de administrações para um arquivo CSV no formato de backup/restauração'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Caminho para o arquivo CSV de saída')
        parser.add_argument('instituicao_cnpj', type=str, nargs='?', help='CNPJ da instituição para filtrar (opcional)')
        parser.add_argument('--periodo_inicio', type=str, help='Data de início do período (YYYY-MM-DD)')
        parser.add_argument('--periodo_fim', type=str, help='Data final do período (YYYY-MM-DD)')
        parser.add_argument('--incluir_todos_dados', action='store_true', help='Inclui todos os dados relacionados, mesmo sem administrações')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        instituicao_cnpj = options['instituicao_cnpj']
        periodo_inicio = options['periodo_inicio']
        periodo_fim = options['periodo_fim']
        incluir_todos_dados = options['incluir_todos_dados']
        
        # Validar e converter datas
        data_inicio = None
        data_fim = None
        
        if periodo_inicio:
            try:
                data_inicio = datetime.strptime(periodo_inicio, '%Y-%m-%d')
                self.stdout.write(self.style.NOTICE(f"Filtrando a partir de: {data_inicio.strftime('%d/%m/%Y')}"))
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Formato de data inválido para período_inicio: {periodo_inicio}. Use YYYY-MM-DD."))
                return
        
        if periodo_fim:
            try:
                data_fim = datetime.strptime(periodo_fim, '%Y-%m-%d')
                # Ajustar para final do dia
                data_fim = data_fim.replace(hour=23, minute=59, second=59)
                self.stdout.write(self.style.NOTICE(f"Filtrando até: {data_fim.strftime('%d/%m/%Y')}"))
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Formato de data inválido para periodo_fim: {periodo_fim}. Use YYYY-MM-DD."))
                return
        
        # Validar instituição
        instituicao = None
        if instituicao_cnpj:
            try:
                instituicao = Instituicao.objects.get(cnpj=instituicao_cnpj)
                self.stdout.write(self.style.NOTICE(f"Exportando dados da instituição: {instituicao.nome} ({instituicao.cnpj})"))
            except Instituicao.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Instituição com CNPJ {instituicao_cnpj} não encontrada."))
                return
        
        # Consultar administrações com filtros aplicados
        query = Administra.objects.all().select_related(
            'profissional', 'morador', 'estoque', 'horario',
            'morador__responsavel', 'estoque__medicamento', 'estoque__apresentacao',
        )
        
        if instituicao:
            query = query.filter(Q(profissional__instituicao=instituicao) | Q(morador__instituicao=instituicao))
        
        if data_inicio:
            query = query.filter(dthr_administracao__gte=data_inicio)
        
        if data_fim:
            query = query.filter(dthr_administracao__lte=data_fim)
        
        administracoes = query.order_by('morador__nome', 'dthr_administracao')
        
        # Se não há administrações com os filtros, verificar se devemos exportar mesmo assim
        if not administracoes.exists():
            if not incluir_todos_dados:
                self.stdout.write(self.style.WARNING("Nenhuma administração encontrada com os filtros especificados."))
                return
            else:
                self.stdout.write(self.style.NOTICE("Nenhuma administração encontrada, mas exportando dados de estoque e moradores conforme solicitado."))
                # Se não há administrações mas queremos incluir todos os dados, precisamos alterar a consulta
                if instituicao:
                    estoques = Estoque.objects.filter(morador__instituicao=instituicao)
                    if estoques.exists():
                        # Usar o primeiro estoque como base para os cabeçalhos
                        self.exportar_dados_sem_administracoes(csv_path, estoques, instituicao)
                        return
        
        # Definir cabeçalhos do CSV (mesmos da importação)
        fieldnames = [
            'Morador', 'Medicamento', 'Uso Contínuo', 'Concentração', 'Prescrição',
            'Data e Hora Prevista da Administração', 'Data e Hora Real da Administração',
            'Erro na Administração', 'Tipo de Erro', 'Enfermeiro Responsável', 'CPF Morador',
            'Data Nascimento Morador', 'CPF Profissional', 'Coren', 'Unidade Prescricao',
            'Unidade Comercial', 'Razao Prescricao Comercial', 'Qtd Disponivel', 'Validade',
            'Dias Uso', 'Hora', 'Aplicado', 'Email Responsável', 'Telefone Responsável',
            'Nome Responsável', 'CPF Responsável', 'Hashcode Responsável', 'Dthr Alteracao'
        ]
        
        if not os.path.dirname(csv_path):
            # Se não tem diretório no caminho, salvar no diretório atual
            csv_path = os.path.join(os.getcwd(), csv_path)
        
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            total = administracoes.count()
            self.stdout.write(self.style.NOTICE(f"Exportando {total} administrações..."))
            
            contador = 0
            for adm in administracoes:
                # Obter os dados de todos os modelos relacionados
                morador = adm.morador
                responsavel = morador.responsavel
                profissional = adm.profissional
                estoque = adm.estoque
                medicamento = estoque.medicamento
                apresentacao = estoque.apresentacao
                horario = adm.horario
                
                # Formatação da data prevista (baseada na data real e hora do horário)
                data_prevista = None
                if adm.dthr_administracao and horario:
                    data_prevista = adm.dthr_administracao.replace(
                        hour=horario.hora, 
                        minute=0, 
                        second=0
                    )
                
                # Criar um registro no formato esperado pelo CSV
                row = {
                    'Morador': morador.nome,
                    'Medicamento': medicamento.principio,
                    'Uso Contínuo': 'True' if estoque.continuo else 'False',
                    'Concentração': estoque.concentracao,
                    'Prescrição': self.formatar_decimal(estoque.prescricao),
                    'Data e Hora Prevista da Administração': self.formatar_datetime(data_prevista),
                    'Data e Hora Real da Administração': self.formatar_datetime(adm.dthr_administracao),
                    'Erro na Administração': 'False',  # Padrão, ajustar se necessário
                    'Tipo de Erro': '',  # Padrão, ajustar se necessário
                    'Enfermeiro Responsável': profissional.nome,
                    'CPF Morador': morador.cpf,
                    'Data Nascimento Morador': self.formatar_date(morador.dt_nascimento),
                    'CPF Profissional': profissional.cpf,
                    'Coren': profissional.coren,
                    'Unidade Prescricao': apresentacao.unidade_prescricao,
                    'Unidade Comercial': apresentacao.unidade_comercial,
                    'Razao Prescricao Comercial': self.formatar_decimal(apresentacao.razao_prescricao_comercial),
                    'Qtd Disponivel': self.formatar_decimal(estoque.qtd_disponivel),
                    'Validade': self.formatar_date(estoque.validade),
                    'Dias Uso': estoque.dias_uso or 0,
                    'Hora': f"{horario.hora:02d}:00:00" if horario else "",
                    'Aplicado': 'Sim' if adm.aplicado else 'Não',
                    'Email Responsável': responsavel.email,
                    'Telefone Responsável': responsavel.telefone,
                    'Nome Responsável': responsavel.nome,
                    'CPF Responsável': responsavel.cpf,
                    'Hashcode Responsável': responsavel.hashcode,
                    'Dthr Alteracao': self.formatar_datetime(estoque.dthr_alteracao)
                }
                
                writer.writerow(row)
                contador += 1
                
                if contador % 100 == 0:
                    self.stdout.write(f"Processadas {contador} de {total} administrações...")
            
        self.stdout.write(self.style.SUCCESS(f"Exportação concluída! {contador} administrações exportadas para {csv_path}"))

    def exportar_dados_sem_administracoes(self, csv_path, estoques, instituicao):
        """Exporta dados de estoque e moradores sem administrações associadas"""
        fieldnames = [
            'Morador', 'Medicamento', 'Uso Contínuo', 'Concentração', 'Prescrição',
            'Data e Hora Prevista da Administração', 'Data e Hora Real da Administração',
            'Erro na Administração', 'Tipo de Erro', 'Enfermeiro Responsável', 'CPF Morador',
            'Data Nascimento Morador', 'CPF Profissional', 'Coren', 'Unidade Prescricao',
            'Unidade Comercial', 'Razao Prescricao Comercial', 'Qtd Disponivel', 'Validade',
            'Dias Uso', 'Hora', 'Aplicado', 'Email Responsável', 'Telefone Responsável',
            'Nome Responsável', 'CPF Responsável', 'Hashcode Responsável', 'Dthr Alteracao'
        ]
          # Obter um profissional padrão para o CSV
        profissional = Profissional.objects.filter(instituicao=instituicao).first()
        if not profissional:
            self.stderr.write(self.style.ERROR("Não foi possível encontrar um profissional para incluir no CSV."))
            return
        
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            total = estoques.count()
            self.stdout.write(self.style.NOTICE(f"Exportando {total} registros de estoque sem administrações..."))
            
            contador = 0
            for estoque in estoques.select_related('morador', 'medicamento', 'apresentacao', 'morador__responsavel'):
                morador = estoque.morador
                responsavel = morador.responsavel
                medicamento = estoque.medicamento
                apresentacao = estoque.apresentacao
                
                # Para cada horário do estoque
                horarios = estoque.horarios.all()
                if not horarios:
                    # Se não tem horários, adiciona uma linha para o estoque
                    row = {
                        'Morador': morador.nome,
                        'Medicamento': medicamento.principio,
                        'Uso Contínuo': 'True' if estoque.continuo else 'False',
                        'Concentração': estoque.concentracao,
                        'Prescrição': self.formatar_decimal(estoque.prescricao),
                        'Data e Hora Prevista da Administração': '',
                        'Data e Hora Real da Administração': '',
                        'Erro na Administração': 'False',
                        'Tipo de Erro': '',
                        'Enfermeiro Responsável': profissional.nome,
                        'CPF Morador': morador.cpf,
                        'Data Nascimento Morador': self.formatar_date(morador.dt_nascimento),
                        'CPF Profissional': profissional.cpf,
                        'Coren': profissional.coren,
                        'Unidade Prescricao': apresentacao.unidade_prescricao,
                        'Unidade Comercial': apresentacao.unidade_comercial,
                        'Razao Prescricao Comercial': self.formatar_decimal(apresentacao.razao_prescricao_comercial),
                        'Qtd Disponivel': self.formatar_decimal(estoque.qtd_disponivel),
                        'Validade': self.formatar_date(estoque.validade),
                        'Dias Uso': estoque.dias_uso or 0,
                        'Hora': '',
                        'Aplicado': 'Não',
                        'Email Responsável': responsavel.email if responsavel else '',
                        'Telefone Responsável': responsavel.telefone if responsavel else '',
                        'Nome Responsável': responsavel.nome if responsavel else '',
                        'CPF Responsável': responsavel.cpf if responsavel else '',
                        'Hashcode Responsável': responsavel.hashcode if responsavel else '',
                        'Dthr Alteracao': self.formatar_datetime(estoque.dthr_alteracao)
                    }
                    writer.writerow(row)
                    contador += 1
                else:
                    # Se tem horários, adiciona uma linha para cada horário
                    for horario in horarios:
                        # Data atual para simular um horário previsto
                        hoje = timezone.now().date()
                        data_prevista = datetime.combine(hoje, datetime.min.time()).replace(hour=horario.hora)
                        
                        row = {
                            'Morador': morador.nome,
                            'Medicamento': medicamento.principio,
                            'Uso Contínuo': 'True' if estoque.continuo else 'False',
                            'Concentração': estoque.concentracao,
                            'Prescrição': self.formatar_decimal(estoque.prescricao),
                            'Data e Hora Prevista da Administração': self.formatar_datetime(data_prevista),
                            'Data e Hora Real da Administração': '',
                            'Erro na Administração': 'False',
                            'Tipo de Erro': '',
                            'Enfermeiro Responsável': profissional.nome,
                            'CPF Morador': morador.cpf,
                            'Data Nascimento Morador': self.formatar_date(morador.dt_nascimento),
                            'CPF Profissional': profissional.cpf,
                            'Coren': profissional.coren,
                            'Unidade Prescricao': apresentacao.unidade_prescricao,
                            'Unidade Comercial': apresentacao.unidade_comercial,
                            'Razao Prescricao Comercial': self.formatar_decimal(apresentacao.razao_prescricao_comercial),
                            'Qtd Disponivel': self.formatar_decimal(estoque.qtd_disponivel),
                            'Validade': self.formatar_date(estoque.validade),
                            'Dias Uso': estoque.dias_uso or 0,
                            'Hora': f"{horario.hora:02d}:00:00",
                            'Aplicado': 'Não',
                            'Email Responsável': responsavel.email if responsavel else '',
                            'Telefone Responsável': responsavel.telefone if responsavel else '',
                            'Nome Responsável': responsavel.nome if responsavel else '',
                            'CPF Responsável': responsavel.cpf if responsavel else '',
                            'Hashcode Responsável': responsavel.hashcode if responsavel else '',
                            'Dthr Alteracao': self.formatar_datetime(estoque.dthr_alteracao)
                        }
                        writer.writerow(row)
                        contador += 1
                
                if contador % 100 == 0:
                    self.stdout.write(f"Processados {contador} registros...")
            
        self.stdout.write(self.style.SUCCESS(f"Exportação concluída! {contador} registros exportados para {csv_path}"))

    def formatar_date(self, date_obj):
        """Formata uma data para o formato YYYY-MM-DD"""
        if date_obj:
            return date_obj.strftime('%Y-%m-%d')
        return ''
    
    def formatar_datetime(self, datetime_obj):
        """Formata um datetime para o formato YYYY-MM-DD HH:MM:SS"""
        if datetime_obj:
            return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        return ''
    
    def formatar_decimal(self, decimal_obj):
        """Formata um valor decimal"""
        if decimal_obj is not None:
            return str(decimal_obj)
        return ''
