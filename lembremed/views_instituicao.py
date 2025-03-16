from django.http import HttpResponse
from django.shortcuts import render
from lembremed.models import Instituicao
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import permission_required
from lembremed.decorators import adiciona_contexto

#teste

#Pagina principal dos instituicoes
#Lista todos os instituicoes
@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_instituicao')
def instituicao_listar(request, contexto_padrao):
	instituicoes = Instituicao.objects.all()
	context = {'lista_instituicoes': instituicoes}

	return render(request, 'instituicao/index.html', {**context, **contexto_padrao})


@permission_required('lembremed.pode_gerenciar_instituicao')
def instituicao_editar(request, pcnpj):
	instituicao = Instituicao.objects.filter(cnpj=pcnpj)[0]
	context = {
		'instituicao': instituicao,
		'usuario': instituicao.usuario,
		}
	return render(request, 'instituicao/cadastro.html', context)


@permission_required('lembremed.pode_gerenciar_instituicao')
def instituicao_cadastrar(request):
	context = {}
	return render(request, 'instituicao/cadastro.html', context)


@permission_required('lembremed.pode_gerenciar_instituicao')
def instituicao_salvar(request):
	if request.method == 'POST':
		# Pegando a variável POST
		pcnpj = request.POST.get('cnpj')
		pnome = request.POST.get('nome')
		pemail = request.POST.get('email')
		psenha = request.POST.get('senha')

		#Verifica se estah editando
		if (request.POST.get('edit')):
			instituicao = Instituicao.objects.get(cnpj=pcnpj)
			instituicao.nome = pnome
			instituicao.save()

			usuario = instituicao.usuario
			usuario.email = pemail
			if (psenha):
				usuario.set_password(psenha)
			usuario.save()

		else:
			usuario = get_user_model().objects.create_user(username=pcnpj, email=pemail, password=psenha)
			usuario.user_permissions.add(Permission.objects.get(codename='pode_gerenciar_morador'))
			usuario.user_permissions.add(Permission.objects.get(codename='pode_gerenciar_profissional'))
			usuario.save()

			instituicao = Instituicao.objects.create(cnpj=pcnpj, nome=pnome, usuario=usuario)

		return HttpResponse("instituicao salvo com sucesso")
	else:
		return HttpResponse("erro por GET no salvar")


@permission_required('lembremed.pode_gerenciar_instituicao')
def instituicao_excluir(request, pcnpj):
	#Verifica se o cnpj existe
	instituicao = Instituicao.objects.get(cnpj=pcnpj)
	if (instituicao):
		instituicao.delete()

		instituicao.usuario.delete()

		return HttpResponse("excluido com sucesso")
	else:
		return HttpResponse("Erro ao localizar cnpj")