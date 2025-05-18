from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection

def relatorios(request):
    """Página principal de relatórios."""
    return render(request, 'lembremed/relatorios.html')

def obter_dados_medicamentos_por_morador(request):
    """API que retorna dados para o gráfico de medicamentos por morador."""
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            m.nome as morador,
            COUNT(DISTINCT e.medicamento_id) as quantidade_medicamentos
        FROM lembremed_morador m
        LEFT JOIN lembremed_estoque e ON e.morador_id = m.cpf
        GROUP BY m.cpf, m.nome
        ORDER BY quantidade_medicamentos DESC
        LIMIT 10
        """)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return JsonResponse(data, safe=False)

def obter_dados_estoque_medicamentos(request):
    """API que retorna dados para o gráfico de estoque de medicamentos."""
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            med.principio as medicamento,
            SUM(e.qtd_disponivel) as quantidade
        FROM lembremed_estoque e
        JOIN lembremed_medicamento med ON med.codigo = e.medicamento_id
        GROUP BY med.principio
        ORDER BY quantidade ASC
        LIMIT 10
        """)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return JsonResponse(data, safe=False)