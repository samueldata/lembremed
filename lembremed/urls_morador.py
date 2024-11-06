from django.urls import re_path
from lembremed import views_morador

urlpatterns = [
    re_path(r'^$', views_morador.morador_listar, name='morador_listar'),
    re_path(r'^editar/(?P<pcpf>[\d\.-]+)/$', views_morador.morador_editar, name='morador_editar'),
    re_path(r'^cadastrar/$', views_morador.morador_cadastrar, name='morador_cadastrar'),
    #Salva novo morador ou morador existente
    re_path(r'^salvar/$', views_morador.morador_salvar, name='morador_salvar'),
    re_path(r'^excluir/(?P<pcpf>[\d\.-]+)/$', views_morador.morador_excluir, name='morador_excluir'),
    re_path(r'^procurar_responsavel/$', views_morador.morador_procurar_responsavel, name='morador_procurar_responsavel'),
]