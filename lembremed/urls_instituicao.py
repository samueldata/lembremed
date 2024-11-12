from django.urls import re_path
from lembremed import views_instituicao

urlpatterns = [
	re_path(r'^$', views_instituicao.instituicao_listar, name='instituicao_listar'),
	re_path(r'^editar/(?P<pcnpj>[\d\.\/-]+)/$', views_instituicao.instituicao_editar, name='instituicao_editar'),
	re_path(r'^cadastrar/$', views_instituicao.instituicao_cadastrar, name='instituicao_cadastrar'),
	#Salva nova instituicao ou instituicao existente
	re_path(r'^salvar/$', views_instituicao.instituicao_salvar, name='instituicao_salvar'),
	re_path(r'^excluir/(?P<pcnpj>[\d\.\/-]+)/$', views_instituicao.instituicao_excluir, name='instituicao_excluir'),
]