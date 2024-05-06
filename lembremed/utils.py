import csv
from .models import Medicamento

def popular_tabela_com_csv():
    #https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string
    with open('static/tabeladeremedios.csv', mode='r', encoding='utf-8-sig') as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv)
        for linha in leitor_csv:
            linha = {chave: valor for chave, valor in linha.items()}
            pprincipio = linha['principio']  # Substitua 'principio' pelo nome correto da coluna no arquivo CSV
            Medicamento.objects.create(principio=pprincipio)
