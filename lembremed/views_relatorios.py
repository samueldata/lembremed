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
            COUNT(med.id) as quantidade_medicamentos
        FROM lembremed_morador m
        LEFT JOIN lembremed_medicamento med ON med.morador_id = m.id
        GROUP BY m.id, m.nome
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
            med.nome as medicamento,
            med.quantidade_atual as quantidade
        FROM lembremed_medicamento med
        ORDER BY med.quantidade_atual ASC
        LIMIT 10
        """)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse(data, safe=False)