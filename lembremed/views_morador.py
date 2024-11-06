from django.http import HttpResponse
from django.shortcuts import render
from .models import Morador, Responsavel, Instituicao, Profissional
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import permission_required
from lembremed.decorators import adiciona_contexto
import requests

#Pagina principal dos moradores
#Lista todos os moradores
@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_morador')
def morador_listar(request, contexto_padrao):
	#Verifica se eh profissional ou instituicao cadastrando
	print("\n", (contexto_padrao['usuario']), "\n\n")
	if (isinstance(contexto_padrao['usuario'], Instituicao)):
		moradores = Morador.objects.filter(instituicao=contexto_padrao['usuario'])

	elif(isinstance(contexto_padrao['usuario'], Profissional)):
		moradores = Morador.objects.filter(instituicao=contexto_padrao['usuario'].instituicao)

	context = {'lista_moradores': moradores}
	return render(request, 'morador/index.html', {**context, **contexto_padrao})


@permission_required('lembremed.pode_gerenciar_morador')
def morador_editar(request, pcpf):
	morador = Morador.objects.filter(cpf=pcpf)[0]
	#return HttpResponse(morador.nome)
	context = {'morador': morador}
	return render(request, 'morador/cadastro.html', context)


@permission_required('lembremed.pode_gerenciar_morador')
def morador_cadastrar(request):
	context = {}
	return render(request, 'morador/cadastro.html', context)


@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_morador')
def morador_salvar(request, contexto_padrao):
	if request.method == 'POST':
		# Pegando a variável POST
		pcpf = request.POST.get('cpf')
		pnome = request.POST.get('nome')
		pdt_nascimento = request.POST.get('dt_nascimento')

		rcpf = request.POST.get('rcpf')
		rnome = request.POST.get('rnome')
		remail = request.POST.get('remail')

		#Verifica se estah editando
		if (request.POST.get('edit')):
			morador = Morador.objects.get(cpf=pcpf)
			morador.nome = pnome
			morador.dt_nascimento = pdt_nascimento

		else:
			morador = Morador(cpf=pcpf, nome=pnome, dt_nascimento=pdt_nascimento)

			responsavel = Responsavel(cpf=rcpf, nome=rnome)
			responsavel.hashcode = requests.get("https://www.uuidgenerator.net/api/version4", headers={"Accept": "application/json"})

		#Verifica se eh profissional ou instituicao cadastrando
		if (isinstance(contexto_padrao['usuario'], Instituicao)):
			morador.instituicao = contexto_padrao['usuario']

		elif(isinstance(contexto_padrao['usuario'], Profissional)):
			morador.instituicao = contexto_padrao['usuario'].instituicao

		morador.save()

		return HttpResponse("Morador salvo com sucesso")
	else:
		return HttpResponse("erro por GET no salvar")


@permission_required('lembremed.pode_gerenciar_morador')
def morador_excluir(request, pcpf):
	#Verifica se o cpf existe
	morador = Morador.objects.get(cpf=pcpf)
	if (morador):
		morador.delete()
		return HttpResponse("excluido com sucesso")
	else:
		return HttpResponse("Erro ao localizar cpf")