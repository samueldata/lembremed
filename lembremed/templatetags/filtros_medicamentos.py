from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def eh_aplicavel(estoque):
	if estoque.continuo:
		return True
	
	if not estoque.dthr_alteracao or not estoque.dias_uso:
		return False
	
	#Aqui o estoque nao eh continuo e tem data de alteracao e dias de uso
	data_limite = estoque.dthr_alteracao.date() + timedelta(days=estoque.dias_uso)
	agora = timezone.localtime(timezone.now()).date()

	from pprint import pprint
	print('\n\n\n\n\n\n\n\n\n\n')
	print('agora')
	pprint(agora)
	print('data_limite')
	pprint(data_limite)
	print('\n\n\n\n')

	return not agora > data_limite