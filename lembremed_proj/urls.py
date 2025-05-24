"""
URL configuration for lembremed_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView  # Importa TemplateView para servir sua landing page
from lembremed.decorators import adiciona_contexto

from django.conf import settings
from django.conf.urls.static import static

from django.shortcuts import render

from lembremed import views_relatorios


#Pagina principal do site
@adiciona_contexto
def index_principal(request, contexto_padrao):
	return render(request, 'index.html', contexto_padrao)


urlpatterns = [
	#Desse jeito não carrega o contexto corretamente, para trazer o nome do usuario
	#path('', adiciona_contexto(TemplateView.as_view(template_name='index.html')), name='index'),
	re_path(r'^$', index_principal, name='index'),
	path('admin/', admin.site.urls),
	path('accounts/', include('django.contrib.auth.urls')),
	path('morador/', include('lembremed.urls_morador')),
	path('profissional/', include('lembremed.urls_profissional')),
	path('medicamento/', include('lembremed.urls_medicamento')),
	path('saida/', include('lembremed.urls_saida')),
	path('instituicao/', include('lembremed.urls_instituicao')),
	path('notificacao/', include('lembremed.urls_notificacao')),
	path('relatorios/', views_relatorios.relatorios, name='relatorios'),
	path('relatorios/exportar-csv/', views_relatorios.exportar_csv, name='exportar_csv'),
	path('relatorios/heatmap-erro-turno/', views_relatorios.heatmap_erro_turno, name='heatmap_erro_turno'),
    path('api/medicamentos-por-morador/', views_relatorios.obter_dados_medicamentos_por_morador, name='dados_medicamentos_por_morador'),
    path('api/estoque-medicamentos/', views_relatorios.obter_dados_estoque_medicamentos, name='dados_estoque_medicamentos'),
    path('api/administracoes-por-periodo/', views_relatorios.obter_dados_administracoes_por_periodo, name='dados_administracoes_por_periodo'),
    path('api/administracoes-por-profissional/', views_relatorios.obter_dados_administracoes_por_profissional, name='dados_administracoes_por_profissional'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
