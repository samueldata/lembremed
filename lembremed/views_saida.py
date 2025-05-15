from django.http import HttpResponse
from django.shortcuts import render
from lembremed.models import Saida, SaidaChoices, Morador, Profissional, Instituicao
from lembremed.decorators import adiciona_contexto
from django.contrib.auth.decorators import permission_required
from django.utils import timezone

#Pagina principal das saidas
#Lista todos as saidas
@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_morador')
def saida_listar(request, pcpf, contexto_padrao):
	#Verifica se eh profissional ou instituicao cadastrando
	if (isinstance(contexto_padrao['usuario'], Instituicao)):
		morador = Morador.objects.filter(cpf=pcpf, instituicao=contexto_padrao['usuario']).first()

	elif(isinstance(contexto_padrao['usuario'], Profissional)):
		morador = Morador.objects.filter(cpf=pcpf, instituicao=contexto_padrao['usuario'].instituicao).first()

	saidas = Saida.objects.filter(morador=morador)
	context = {
		'lista_saidas': saidas,
		'morador': morador,
		'tem_saida_aberta': any(s.dt_fim is None for s in saidas),
	}

	return render(request, 'saida/index.html', {**context, **contexto_padrao})


@adiciona_contexto
@permission_required('lembremed.pode_medicar_morador')
def saida_editar(request, pcpf, pcodigo, contexto_padrao):
	morador = Morador.objects.filter(cpf=pcpf).first()
	saida = Saida.objects.get(codigo=pcodigo, morador__cpf=pcpf)
	context = {
		'saida': saida,
		'morador': morador,
		'saida_choices': SaidaChoices.choices,
		}
	return render(request, 'saida/cadastro.html', context)


@permission_required('lembremed.pode_medicar_morador')
def saida_cadastrar(request, pcpf):
	morador = Morador.objects.filter(cpf=pcpf).first()
	context = {
		'morador': morador,
		'saida_choices': SaidaChoices.choices,
		}
	return render(request, 'saida/cadastro.html', context)


@permission_required('lembremed.pode_medicar_morador')
def saida_salvar(request, pcpf):
	if request.method == 'POST':
		# Pegando a variável POST
		pcodigo = request.POST.get('codigo')
		ptipo_saida = request.POST.get('tipo_saida')

		#Verifica se estah editando
		if (request.POST.get('edit')):
			saida = Saida.objects.filter(codigo=pcodigo)[0]
			saida.dt_fim = timezone.localtime(timezone.now())

			saida.save()

		else:
			saida = Saida.objects.create(
				morador = Morador.objects.get(cpf=pcpf),
				dt_inicio = timezone.localtime(timezone.now()),
				tipo = ptipo_saida,  # já é 'TP', 'MD' ou 'MO'
			)

		return HttpResponse("Saida salvo com sucesso")
	else:
		return HttpResponse("erro por GET no salvar")


@permission_required('lembremed.pode_medicar_morador')
def saida_excluir(request, pcpf):
	return HttpResponse("erro por GET no salvar")