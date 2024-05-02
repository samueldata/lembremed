from django.urls import re_path
from . import views_profissional

urlpatterns = [
    re_path(r'^$', views_profissional.profissional_listar, name='profissional_listar'),
    re_path(r'^editar/(?P<pcpf>\d+)/$', views_profissional.profissional_editar, name='profissional_editar'),
    re_path(r'^cadastrar/$', views_profissional.profissional_cadastrar, name='profissional_cadastrar'),
    #Salva novo profissional ou profissional existente
    re_path(r'^salvar/$', views_profissional.profissional_salvar, name='profissional_salvar'),
    re_path(r'^excluir/(?P<pcpf>\d+)/$', views_profissional.profissional_excluir, name='profissional_excluir'),
]