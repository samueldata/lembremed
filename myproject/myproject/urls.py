"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# myproject/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # Importa TemplateView para servir sua landing page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),  # Página inicial
    path('moradores/', include('gestao_moradores.urls')),  # App de gestão de moradores
    path('profissionais/', include('gestao_profissionais.urls')),  # App de gestão de profissionais
    path('medicacoes/', include('controle_medicamentos.urls')),  # App de controle de medicamentos
    path('estoque/', include('gestao_estoque.urls')),  # App de gestão de estoque
    # ... outros caminhos URL ...
]

