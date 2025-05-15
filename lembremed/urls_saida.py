from django.urls import re_path
from lembremed import views_saida

urlpatterns = [
	re_path(r'^(?P<pcpf>[\d\.-]+)/$', views_saida.saida_listar, name='saida_listar'),
	re_path(r'^(?P<pcpf>[\d\.-]+)/editar/(?P<pcodigo>\d+)/$', views_saida.saida_editar, name='saida_editar'),
	re_path(r'^(?P<pcpf>[\d\.-]+)/cadastrar/$', views_saida.saida_cadastrar, name='saida_cadastrar'),
	#Salva nova saida ou saida existente
	re_path(r'^(?P<pcpf>[\d\.-]+)/salvar/$', views_saida.saida_salvar, name='saida_salvar'),
	re_path(r'^(?P<pcpf>[\d\.-]+)/excluir/(?P<pcodigo>\d+)/$', views_saida.saida_excluir, name='saida_excluir'),
]