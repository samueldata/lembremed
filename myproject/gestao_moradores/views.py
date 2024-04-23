# gestao_moradores/views.py
from django.shortcuts import render

def index(request):
    # Esta função lida com a lógica para a página inicial dos moradores.
    return render(request, 'gestao_moradores/index.html')
    # O Django irá procurar o arquivo index.html dentro de gestao_moradores/templates/gestao_moradores/

