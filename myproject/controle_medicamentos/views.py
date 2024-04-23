# controle_medicamentos/views.py
from django.shortcuts import render

def index(request):

    return render(request, 'controle_medicamentos/index.html')
    
