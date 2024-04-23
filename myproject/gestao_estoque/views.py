# gestao_estoque/views.py
from django.shortcuts import render

def index(request):

    return render(request, 'gestao_estoque/index.html')


