from django.urls import re_path
from lembremed import views_notificacao

urlpatterns = [
	re_path(r'^$', views_notificacao.notificacao_listar, name='notificacao_listar'),
]