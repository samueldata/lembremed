from functools import wraps
from lembremed.models import Profissional, Instituicao, Morador, Medicamento, Estoque
from datetime import date, timedelta

def adiciona_contexto(func):
	@wraps(func)
	def wrapper(request, *args, **kwargs):

		#Cria a variavel com valor padrao
		contexto_padrao = {'usuario': {'nome': '-usuario-'},
					 		'estoque_acabando': [],
					 		'estoque_vencendo': []}

		#Verifica se o usuario estah logado
		if (request.user.is_authenticated):
			#Cria a variavel com valor padrao
			contexto_padrao = {'usuario': {'nome': 'Administrador'}}

			#verifica se o usuario eh profissional
			usuario = Profissional.objects.filter(usuario=request.user).first()
			if (usuario):
				contexto_padrao = {'usuario': usuario}
				contexto_padrao['instituicao'] = usuario.instituicao
			else:
				usuario = Instituicao.objects.filter(usuario=request.user).first()
				if (usuario):
					contexto_padrao = {'usuario': usuario}
					contexto_padrao['instituicao'] = usuario

			#Verifica se eh uma instituicao ou profissional
			if (contexto_padrao.get('instituicao', None)):
				#Verifica se tem medicamento a vencer ou a faltar
				contexto_padrao['estoque_acabando'] = []
				estoque = Estoque.objects.filter(morador__instituicao=contexto_padrao['instituicao'])
				for item in estoque:
					if (item.estimativa_duracao() <= 7):
						contexto_padrao['estoque_acabando'].append(item)
				contexto_padrao['estoque_vencendo'] = Estoque.objects.filter(validade__lte=date.today() + timedelta(days=7))



		# Chame a função original da view e adicione o contexto
		return func(request, contexto_padrao=contexto_padrao, *args, **kwargs)
	return wrapper
