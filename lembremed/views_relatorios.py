from django.shortcuts import render
import pandas as pd
import plotly.express as px
import os
from django.http import JsonResponse
from django.db import connection
import json
from datetime import datetime
import time
from django.conf import settings
from decimal import Decimal

# Caminho onde os arquivos de cache serão armazenhados
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

@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_profissional')
def exportar_csv(request, contexto_padrao):
    """Gera e disponibiliza para download um arquivo CSV com dados de administrações."""
    import tempfile
    import os
    from django.http import FileResponse
    from django.core.management import call_command
    from django.contrib import messages
    from django.shortcuts import redirect
    from io import StringIO
    
    # Obter parâmetros do request
    instituicao = contexto_padrao.get('usuario')
    periodo_inicio = request.GET.get('inicio')
    periodo_fim = request.GET.get('fim')
    
    # Criar arquivo temporário para armazenar o CSV
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
        temp_path = temp_file.name
    
    try:
        # Capturar a saída do comando
        output = StringIO()
        
        # Construir argumentos para o comando
        args = [temp_path]
        if instituicao and instituicao.cnpj:
            args.append(instituicao.cnpj)
        
        kwargs = {'stdout': output}
        if periodo_inicio:
            kwargs['periodo_inicio'] = periodo_inicio
        if periodo_fim:
            kwargs['periodo_fim'] = periodo_fim
        
        # Incluir todos os dados mesmo sem administrações
        kwargs['incluir_todos_dados'] = True
        
        # Executar o comando de exportação
        call_command('exportar_administracoes', *args, **kwargs)
        
        # Nome do arquivo para download
        filename = 'administracoes'
        if periodo_inicio:
            filename += f"_de_{periodo_inicio}"
        if periodo_fim:
            filename += f"_ate_{periodo_fim}"
        filename += '.csv'
        
        # Retornar o arquivo como uma resposta para download
        response = FileResponse(open(temp_path, 'rb'), as_attachment=True, filename=filename)
        
        # Configurar para deletar o arquivo temporário após enviar a resposta
        response._resource_closers.append(lambda: os.unlink(temp_path))
        
        return response
        
    except Exception as e:
        # Em caso de erro, deletar o arquivo temporário e mostrar mensagem
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        messages.error(request, f"Erro ao gerar o arquivo CSV: {str(e)}")
        return redirect('relatorios')

def grafico_heatmap(request):
    """Gera o gráfico de heatmap para administrações por horário e profissional."""
    try:
        # Consulta os dados necessários
        dados = consultar_administracoes_por_horario_profissional()
        
        # Cria o DataFrame para o gráfico
        df = pd.DataFrame(dados)
        
        # Gera o gráfico de heatmap
        fig = px.density_heatmap(df, x="hora", y="profissional", z="quantidade",
                                  labels={"hora": "Hora do Dia", "profissional": "Profissional", "quantidade": "Quantidade de Administrações"},
                                  title="Heatmap de Administrações por Horário e Profissional")
        
        # Salva o gráfico como uma imagem estática
        caminho_imagem = os.path.join(CACHE_DIR, "heatmap_administracoes.png")
        fig.write_image(caminho_imagem)
        
        # Retorna a imagem gerada
        return JsonResponse({"url_imagem": request.build_absolute_uri(caminho_imagem)})
    except Exception as e:
        print(f"Erro ao gerar gráfico de heatmap: {str(e)}")
        return JsonResponse({"erro": str(e)}, status=500)

def consultar_administracoes_por_horario_profissional():
    """Executa consulta SQL para obter administrações por horário e profissional."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT 
                TO_CHAR(a.dthr_administracao, 'HH24:MI') as hora,
                p.nome as profissional,
                COUNT(*) as quantidade
            FROM lembremed_administra a
            JOIN lembremed_profissional p ON p.cpf = a.profissional_id
            WHERE a.dthr_administracao IS NOT NULL
            GROUP BY hora, p.nome
            ORDER BY hora, p.nome
            """)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results
    except Exception as e:
        # Em caso de erro, retorna lista vazia
        return []

@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_profissional')
def heatmap_erro_turno(request, contexto_padrao):
    """Gera um heatmap mostrando a proporção de tipos de erro por turno."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN EXTRACT(HOUR FROM h.hora) BETWEEN 0 AND 5 THEN 'Madrugada (0h-5h)'
                        WHEN EXTRACT(HOUR FROM h.hora) BETWEEN 6 AND 11 THEN 'Manhã (6h-11h)'
                        WHEN EXTRACT(HOUR FROM h.hora) BETWEEN 12 AND 17 THEN 'Tarde (12h-17h)'
                        WHEN EXTRACT(HOUR FROM h.hora) BETWEEN 18 AND 23 THEN 'Noite (18h-23h)'
                    END as turno,
                    CASE
                        WHEN a.dthr_administracao IS NULL THEN 'Não Administrado'
                        WHEN EXTRACT(HOUR FROM a.dthr_administracao) > h.hora THEN 'Atraso'
                        WHEN EXTRACT(HOUR FROM a.dthr_administracao) < h.hora THEN 'Antecipado'
                        ELSE 'No Horário'
                    END as tipo_erro,
                    COUNT(*) as contagem
                FROM lembremed_administra a
                JOIN lembremed_horario h ON h.codigo = a.horario_id
                GROUP BY turno, tipo_erro
                ORDER BY 
                    CASE 
                        WHEN turno = 'Madrugada (0h-5h)' THEN 1
                        WHEN turno = 'Manhã (6h-11h)' THEN 2
                        WHEN turno = 'Tarde (12h-17h)' THEN 3
                        WHEN turno = 'Noite (18h-23h)' THEN 4
                    END,
                    tipo_erro
            """)
            
            dados = [
                {
                    'turno': row[0],
                    'Tipo de Erro': row[1],
                    'Contagem': row[2]
                }
                for row in cursor.fetchall()
            ]

        # Se não houver dados, criar dados de exemplo
        if not dados:
            turnos = ['Madrugada (0h-5h)', 'Manhã (6h-11h)', 'Tarde (12h-17h)', 'Noite (18h-23h)']
            tipos_erro = ['Não Administrado', 'Atraso', 'Antecipado', 'No Horário']
            dados = [
                {
                    'turno': turno,
                    'Tipo de Erro': tipo,
                    'Contagem': 0
                }
                for turno in turnos
                for tipo in tipos_erro
            ]

        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Calcular proporções
        total_por_turno = df.groupby('turno')['Contagem'].transform('sum')
        df['Proporcao'] = df['Contagem'] / total_por_turno
        df['Proporcao'] = df['Proporcao'].fillna(0)  # Substituir NaN por 0

        # Criar o heatmap
        fig = px.density_heatmap(
            df,
            x='Tipo de Erro',
            y='turno',
            z='Proporcao',
            color_continuous_scale='Blues',
            text_auto='.1%',
            title='Proporção de Tipos de Erro por Turno',
            labels={'turno': 'Turno', 'Proporcao': 'Proporção'}
        )

        fig.update_layout(
            yaxis_title='Turno',
            xaxis_title='Tipo de Erro',
            height=400
        )

        html_grafico = fig.to_html(full_html=False)
        return render(request, 'lembremed/heatmap_turno_erro.html', {**contexto_padrao, 'grafico': html_grafico})
        
    except Exception as e:
        print(f"Erro ao gerar heatmap de erros por turno: {str(e)}")
        return JsonResponse({"erro": str(e)}, status=500)