from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
import json
import os
from datetime import datetime
import time
from django.conf import settings
from decimal import Decimal

# Caminho onde os arquivos de cache serão armazenados
CACHE_DIR = os.path.join(settings.BASE_DIR, 'cache')
# Tempo máximo de cache em segundos (4 horas)
CACHE_MAX_AGE = 4 * 60 * 60

# Garante que o diretório de cache exista
os.makedirs(CACHE_DIR, exist_ok=True)

# Classe para serializar Decimal em JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def arquivo_cache_valido(arquivo):
    """Verifica se um arquivo de cache existe e está válido (não expirado)."""
    try:
        if not os.path.exists(arquivo):
            return False
        
        # Verifica a idade do arquivo
        idade_arquivo = time.time() - os.path.getmtime(arquivo)
        
        # Verifica se o arquivo pode ser carregado como JSON válido
        with open(arquivo, 'r') as f:
            json.load(f)
            
        return idade_arquivo < CACHE_MAX_AGE
    except (json.JSONDecodeError, IOError, OSError):
        # Se o arquivo não puder ser carregado como JSON ou tiver qualquer erro de IO
        return False

from lembremed.decorators import adiciona_contexto
from django.contrib.auth.decorators import permission_required

@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_profissional')
def relatorios(request, contexto_padrao):
    """Página principal de relatórios."""
    # Força a atualização dos caches se solicitado pela URL
    if request.GET.get('atualizar') == '1':
        atualizar_cache_relatorios()
    else:
        # Verifica se os arquivos de cache existem, se não existirem, cria-os
        arquivos_cache = [
            os.path.join(CACHE_DIR, 'medicamentos_por_morador.json'),
            os.path.join(CACHE_DIR, 'estoque_medicamentos.json'),
            os.path.join(CACHE_DIR, 'administracoes_por_periodo.json'),
            os.path.join(CACHE_DIR, 'administracoes_por_profissional.json')
        ]
        
        # Se algum arquivo não existir ou não estiver válido, atualiza todos
        for arquivo in arquivos_cache:
            if not arquivo_cache_valido(arquivo):
                print(f"Arquivo de cache inválido ou inexistente: {arquivo}")
                atualizar_cache_relatorios()
                break
    
    return render(request, 'lembremed/relatorios.html', contexto_padrao)

def atualizar_cache_relatorios():
    """Atualiza todos os caches de relatórios."""
    # Gera e salva dados de medicamentos por morador
    dados = consultar_medicamentos_por_morador()
    arquivo = os.path.join(CACHE_DIR, 'medicamentos_por_morador.json')
    with open(arquivo, 'w') as f:
        json.dump(dados, f, cls=DecimalEncoder)
    
    # Gera e salva dados de estoque de medicamentos
    dados = consultar_estoque_medicamentos()
    arquivo = os.path.join(CACHE_DIR, 'estoque_medicamentos.json')
    with open(arquivo, 'w') as f:
        json.dump(dados, f, cls=DecimalEncoder)
    
    # Gera e salva dados de administrações por período
    dados = consultar_administracoes_por_periodo()
    arquivo = os.path.join(CACHE_DIR, 'administracoes_por_periodo.json')
    with open(arquivo, 'w') as f:
        json.dump(dados, f, cls=DecimalEncoder)
    
    # Gera e salva dados de administrações por profissional
    dados = consultar_administracoes_por_profissional()
    arquivo = os.path.join(CACHE_DIR, 'administracoes_por_profissional.json')
    with open(arquivo, 'w') as f:
        json.dump(dados, f, cls=DecimalEncoder)

def consultar_medicamentos_por_morador():
    """Executa a consulta SQL para obter medicamentos por morador."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT 
                m.nome as morador,
                COUNT(DISTINCT e.medicamento_id) as quantidade_medicamentos
            FROM lembremed_morador m
            LEFT JOIN lembremed_estoque e ON e.morador_id = m.cpf
            GROUP BY m.cpf, m.nome
            HAVING COUNT(DISTINCT e.medicamento_id) > 0
            ORDER BY quantidade_medicamentos DESC
            LIMIT 10
            """)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Se não retornar dados, retorna um exemplo
            if not results:
                results = [{"morador": "Sem dados disponíveis", "quantidade_medicamentos": 0}]
            
            return results
    except Exception as e:
        # Em caso de erro, retorna dados de exemplo
        return [{"morador": "Erro na consulta", "quantidade_medicamentos": 0}]

def consultar_estoque_medicamentos():
    """Executa a consulta SQL para obter estoque de medicamentos."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT 
                med.principio as medicamento,
                CAST(SUM(e.qtd_disponivel) AS FLOAT) as quantidade
            FROM lembremed_estoque e
            JOIN lembremed_medicamento med ON med.codigo = e.medicamento_id
            GROUP BY med.principio
            HAVING SUM(e.qtd_disponivel) > 0
            ORDER BY quantidade ASC
            LIMIT 10
            """)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Se não retornar dados, retorna um exemplo
            if not results:
                results = [{"medicamento": "Sem dados disponíveis", "quantidade": 0}]
            
            return results
    except Exception as e:
        # Em caso de erro, retorna dados de exemplo
        return [{"medicamento": "Erro na consulta", "quantidade": 0}]

def consultar_administracoes_por_periodo():
    """Executa consulta SQL para obter administrações agrupadas por período do dia."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT 
                CASE 
                    WHEN EXTRACT(HOUR FROM a.dthr_administracao) BETWEEN 6 AND 11 THEN 'Manhã (6h-11h)'
                    WHEN EXTRACT(HOUR FROM a.dthr_administracao) BETWEEN 12 AND 17 THEN 'Tarde (12h-17h)'
                    WHEN EXTRACT(HOUR FROM a.dthr_administracao) BETWEEN 18 AND 23 THEN 'Noite (18h-23h)'
                    ELSE 'Madrugada (0h-5h)'
                END as periodo,
                COUNT(*) as quantidade
            FROM lembremed_administra a
            WHERE a.dthr_administracao IS NOT NULL
            GROUP BY periodo
            ORDER BY 
                CASE 
                    WHEN periodo = 'Madrugada (0h-5h)' THEN 1
                    WHEN periodo = 'Manhã (6h-11h)' THEN 2
                    WHEN periodo = 'Tarde (12h-17h)' THEN 3
                    WHEN periodo = 'Noite (18h-23h)' THEN 4
                END
            """)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Se não retornar dados, criar dados de exemplo
            if not results:
                results = [
                    {"periodo": "Manhã (6h-11h)", "quantidade": 0},
                    {"periodo": "Tarde (12h-17h)", "quantidade": 0},
                    {"periodo": "Noite (18h-23h)", "quantidade": 0},
                    {"periodo": "Madrugada (0h-5h)", "quantidade": 0}
                ]
            
            return results
    except Exception as e:
        # Em caso de erro, retorna dados de exemplo
        return [
            {"periodo": "Manhã (6h-11h)", "quantidade": 0},
            {"periodo": "Tarde (12h-17h)", "quantidade": 0},
            {"periodo": "Noite (18h-23h)", "quantidade": 0},
            {"periodo": "Madrugada (0h-5h)", "quantidade": 0}
        ]

def consultar_administracoes_por_profissional():
    """Executa consulta SQL para obter administrações por profissional."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT 
                p.nome as profissional,
                COUNT(*) as quantidade_administracoes
            FROM lembremed_administra a
            JOIN lembremed_profissional p ON p.cpf = a.profissional_id
            GROUP BY p.cpf, p.nome
            HAVING COUNT(*) > 0
            ORDER BY quantidade_administracoes DESC
            LIMIT 10
            """)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Se não retornar dados, criar dados de exemplo
            if not results:
                results = [
                    {"profissional": "Sem dados disponíveis", "quantidade_administracoes": 0}
                ]
            
            return results
    except Exception as e:
        # Em caso de erro, retorna dados de exemplo
        return [{"profissional": "Erro na consulta", "quantidade_administracoes": 0}]

def obter_dados_medicamentos_por_morador(request):
    """API que retorna dados para o gráfico de medicamentos por morador."""
    try:
        arquivo_cache = os.path.join(CACHE_DIR, 'medicamentos_por_morador.json')
        
        # Verifica se é necessário atualizar o cache
        if not arquivo_cache_valido(arquivo_cache) or request.GET.get('atualizar') == '1':
            # Gera novos dados e salva no cache
            dados = consultar_medicamentos_por_morador()
            with open(arquivo_cache, 'w') as f:
                json.dump(dados, f, cls=DecimalEncoder)
        else:
            # Carrega dados do cache
            with open(arquivo_cache, 'r') as f:
                dados = json.load(f)
        
        # Debug: registra dados que serão retornados
        print(f"Dados medicamentos_por_morador: {dados}")
        
        # Força a conversão explícita de todos os valores numéricos para float
        for item in dados:
            if 'quantidade_medicamentos' in item:
                item['quantidade_medicamentos'] = float(item['quantidade_medicamentos'])
        
        return JsonResponse(dados, safe=False)
    except Exception as e:
        # Em caso de erro, retorna um array vazio
        print(f"Erro ao obter dados de medicamentos por morador: {str(e)}")
        return JsonResponse([], safe=False)

def obter_dados_estoque_medicamentos(request):
    """API que retorna dados para o gráfico de estoque de medicamentos."""
    try:
        arquivo_cache = os.path.join(CACHE_DIR, 'estoque_medicamentos.json')
        
        # Verifica se é necessário atualizar o cache
        if not arquivo_cache_valido(arquivo_cache) or request.GET.get('atualizar') == '1':
            # Gera novos dados e salva no cache
            dados = consultar_estoque_medicamentos()
            with open(arquivo_cache, 'w') as f:
                json.dump(dados, f, cls=DecimalEncoder)
        else:
            # Carrega dados do cache
            with open(arquivo_cache, 'r') as f:
                dados = json.load(f)
        
        # Debug: registra dados que serão retornados
        print(f"Dados estoque_medicamentos: {dados}")
        
        # Força a conversão explícita de todos os valores numéricos para float
        for item in dados:
            if 'quantidade' in item:
                item['quantidade'] = float(item['quantidade'])
        
        return JsonResponse(dados, safe=False)
    except Exception as e:
        # Em caso de erro, retorna um array vazio
        print(f"Erro ao obter dados de estoque de medicamentos: {str(e)}")
        return JsonResponse([], safe=False)

def obter_dados_administracoes_por_periodo(request):
    """API que retorna dados para o gráfico de administrações por período do dia."""
    try:
        arquivo_cache = os.path.join(CACHE_DIR, 'administracoes_por_periodo.json')
        
        # Verifica se é necessário atualizar o cache
        if not arquivo_cache_valido(arquivo_cache) or request.GET.get('atualizar') == '1':
            # Gera novos dados e salva no cache
            dados = consultar_administracoes_por_periodo()
            with open(arquivo_cache, 'w') as f:
                json.dump(dados, f, cls=DecimalEncoder)
        else:
            # Carrega dados do cache
            with open(arquivo_cache, 'r') as f:
                dados = json.load(f)
        
        # Debug: registra dados que serão retornados
        print(f"Dados administracoes_por_periodo: {dados}")
        
        # Força a conversão explícita de todos os valores numéricos para float
        for item in dados:
            if 'quantidade' in item:
                item['quantidade'] = float(item['quantidade'])
        
        return JsonResponse(dados, safe=False)
    except Exception as e:
        # Em caso de erro, retorna dados de exemplo
        print(f"Erro ao obter dados de administrações por período: {str(e)}")
        return JsonResponse([
            {"periodo": "Manhã (6h-11h)", "quantidade": 0},
            {"periodo": "Tarde (12h-17h)", "quantidade": 0},
            {"periodo": "Noite (18h-23h)", "quantidade": 0},
            {"periodo": "Madrugada (0h-5h)", "quantidade": 0}
        ], safe=False)

def obter_dados_administracoes_por_profissional(request):
    """API que retorna dados para o gráfico de administrações por profissional."""
    try:
        arquivo_cache = os.path.join(CACHE_DIR, 'administracoes_por_profissional.json')
        
        # Verifica se é necessário atualizar o cache
        if not arquivo_cache_valido(arquivo_cache) or request.GET.get('atualizar') == '1':
            # Gera novos dados e salva no cache
            dados = consultar_administracoes_por_profissional()
            with open(arquivo_cache, 'w') as f:
                json.dump(dados, f, cls=DecimalEncoder)
        else:
            # Carrega dados do cache
            with open(arquivo_cache, 'r') as f:
                dados = json.load(f)
        
        # Debug: registra dados que serão retornados
        print(f"Dados administracoes_por_profissional: {dados}")
        
        # Força a conversão explícita de todos os valores numéricos para float
        for item in dados:
            if 'quantidade_administracoes' in item:
                item['quantidade_administracoes'] = float(item['quantidade_administracoes'])
        
        return JsonResponse(dados, safe=False)
    except Exception as e:
        # Em caso de erro, retorna dados de exemplo
        print(f"Erro ao obter dados de administrações por profissional: {str(e)}")
        return JsonResponse([
            {"profissional": "Sem dados disponíveis", "quantidade_administracoes": 0}
        ], safe=False)