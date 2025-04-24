from django.urls import re_path
from lembremed import views_medicamento

urlpatterns = [
	re_path(r'^(?P<pcpf>[\d\.-]+)/$', views_medicamento.medicamento_listar, name='medicamento_listar'),
	re_path(r'^(?P<pcpf>[\d\.-]+)/editar/(?P<pcodigo>\d+)/$', views_medicamento.medicamento_editar, name='medicamento_editar'),
	re_path(r'^(?P<pcpf>[\d\.-]+)/cadastrar/$', views_medicamento.medicamento_cadastrar, name='medicamento_cadastrar'),
	#Salva novo medicamento ou medicamento existente
	re_path(r'^(?P<pcpf>[\d\.-]+)/salvar/$', views_medicamento.medicamento_salvar, name='medicamento_salvar'),
	re_path(r'^(?P<pcpf>[\d\.-]+)/excluir/(?P<pcodigo>\d+)/$', views_medicamento.medicamento_excluir, name='medicamento_excluir'),
	re_path(r'^(?P<pcpf>[\d\.-]+)/administrar/(?P<pcodigo>\d+)/$', views_medicamento.medicamento_administrar, name='medicamento_administrar'),
]