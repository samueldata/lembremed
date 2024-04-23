# gestao_profissionais/views.py
from django.shortcuts import render

def index(request):

    return render(request, 'gestao_profissionais/index.html')


