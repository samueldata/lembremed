from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from lembremed.models import Estoque, Medicamento, Administra, Morador, Profissional, Apresentacao, Instituicao
from lembremed.decorators import adiciona_contexto
from django.contrib.auth.decorators import permission_required
from datetime import datetime
from django.core.mail import send_mail
import re
from decimal import Decimal
import requests
from django.conf import settings


def verificar_apresentacoes():
	qtd_apresentacoes = Apresentacao.objects.count()
	if (qtd_apresentacoes == 0):
		Apresentacao.objects.create(
			unidade_prescricao = 'gota(s)',
			unidade_comercial = 'ml(s)',
			razao_prescricao_comercial = 22,
		)
		Apresentacao.objects.create(
			unidade_prescricao = 'ml(s)',
			unidade_comercial = 'ml(s)',
			razao_prescricao_comercial = 1,
		)
		Apresentacao.objects.create(
			unidade_prescricao = 'comprimido(s)',
			unidade_comercial = 'comprimido(s)',
			razao_prescricao_comercial = 1,
		)
		Apresentacao.objects.create(
			unidade_prescricao = 'dose(s)',
			unidade_comercial = 'dose(s)',
			razao_prescricao_comercial = 1,
		)

#Pagina principal dos medicamentos
#Lista todos os medicamentos
@adiciona_contexto
@permission_required('lembremed.pode_gerenciar_morador')
def medicamento_listar(request, pcpf, contexto_padrao):
	#Verifica se tem os tipos de apresentacao cadastrados
	verificar_apresentacoes()

	#Verifica se eh profissional ou instituicao cadastrando
	if (isinstance(contexto_padrao['usuario'], Instituicao)):
		morador = Morador.objects.filter(cpf=pcpf, instituicao=contexto_padrao['usuario']).first()

	elif(isinstance(contexto_padrao['usuario'], Profissional)):
		morador = Morador.objects.filter(cpf=pcpf, instituicao=contexto_padrao['usuario'].instituicao).first()

	estoques = Estoque.objects.filter(morador=morador)

	estoques_administrados = []
	for estoque in estoques:
		ultima_administracao = Administra.objects.filter(estoque=estoque).order_by('-dthr_administracao').first()
		estoques_administrados.append({ #Cria o objeto com o estoque e sua ultima administracao
			'estoque': estoque,
			'ultima_administracao': ultima_administracao,
			'duracao': ((estoque.qtd_disponivel * estoque.apresentacao.razao_prescricao_comercial) / (estoque.frequencia * estoque.prescricao)) if estoque.qtd_disponivel and estoque.frequencia and estoque.apresentacao.razao_prescricao_comercial and estoque.prescricao else 0
		})

	context = {'lista_estoques': estoques_administrados, 'morador': morador}

	return render(request, 'medicamento/index.html', {**context, **contexto_padrao})


@permission_required('lembremed.pode_medicar_morador')
def medicamento_editar(request, pcpf, pcodigo):
	estoque = Estoque.objects.get(codigo=pcodigo, morador__cpf=pcpf)

	arr_medicamentos = Medicamento.objects.all().order_by('principio')
	arr_apresentacoes = Apresentacao.objects.all().order_by('unidade_prescricao')

	context = {
		'estoque': estoque,
		'arr_medicamentos': arr_medicamentos,
		'arr_apresentacoes': arr_apresentacoes,
		}
	return render(request, 'medicamento/cadastro.html', context)


@permission_required('lembremed.pode_medicar_morador')
def medicamento_cadastrar(request, pcpf):
	arr_medicamentos = Medicamento.objects.all().order_by('principio')
	arr_apresentacoes = Apresentacao.objects.all().order_by('unidade_prescricao')

	context = {
		'cpf': pcpf,
		'arr_medicamentos': arr_medicamentos,
		'arr_apresentacoes': arr_apresentacoes,
		}
	return render(request, 'medicamento/cadastro.html', context)


@permission_required('lembremed.pode_medicar_morador')
def medicamento_salvar(request, pcpf):
	if request.method == 'POST':
		# Pegando a variável POST
		pcodigo = request.POST.get('codigo')
		pcodigo_medicamento = request.POST.get('codigo_medicamento')
		papresentacao = Apresentacao.objects.get(codigo=request.POST.get('apresentacao'))
		pconcentracao = request.POST.get('concentracao')
		pvalidade = request.POST.get('validade')
		pprescricao = Decimal(request.POST.get('prescricao'))
		pprescricao = pprescricao if pprescricao > 0 else 1
		pfrequencia = Decimal(request.POST.get('frequencia'))
		pfrequencia = pfrequencia if pfrequencia > 0 else 1
		phorarios = request.POST.get('horarios')
		pqtd_disponivel = request.POST.get('qtd_disponivel')
		pqtd_alterar = request.POST.get('qtd_alterar')

		#Verifica se estah editando
		if (request.POST.get('edit')):
			estoque = Estoque.objects.filter(codigo=pcodigo)[0]
			estoque.medicamento = Medicamento.objects.get(codigo=pcodigo_medicamento)
			estoque.apresentacao = papresentacao
			estoque.concentracao = pconcentracao
			estoque.validade = pvalidade
			estoque.prescricao = pprescricao
			estoque.frequencia = pfrequencia
			estoque.horarios = phorarios
			pqtd_alterar = re.findall(r'^(\+|\-)(\d+|\d+\.\d+)$', pqtd_alterar)

			if (len(pqtd_alterar) == 1):
				psinal, pqtd_alterar = pqtd_alterar[0]
				estoque.qtd_disponivel = estoque.qtd_disponivel if estoque.qtd_disponivel else Decimal('0')
				if (psinal == '+'):
					estoque.qtd_disponivel += Decimal(pqtd_alterar)
				else:
					estoque.qtd_disponivel -= Decimal(pqtd_alterar)
			estoque.save()

			if (estoque.estimativa_duracao() <= 7):
				#Verifica se o responsavel tem telegram cadastrado
				if (estoque.morador.responsavel.telegram_id):
					url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
					dados_post = {
						'chat_id': estoque.morador.responsavel.telegram_id,
						'text': f"Medicamento {estoque.medicamento.principio} {estoque.apresentacao.unidade_prescricao} recém administrado tem 7 dias ou menos de estoque\nVerifique a necessidade de uma nova aquisição"
					}

					x = requests.post(url, json = dados_post)

					#requests.get(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage?chat_id={estoque.morador.responsavel.telegram_id}&text=Medicamento {estoque.medicamento.principio} {estoque.apresentacao.unidade_prescricao} recém administrado tem 7 dias ou menos de estoque")
				if (estoque.morador.responsavel.email):
					
					mensagem = render_to_string('email_templates/basic_email.html', {
							'title': "Medicamento acabando - Lembremed",
							'message': f"Olá {estoque.morador.responsavel.nome.split()[0]}." 
										f"\n<br />O medicamento {estoque.medicamento.principio} {estoque.apresentacao.unidade_prescricao} foi recém administrado agora tem 7 dias ou menos de estoque disponível."
										f"\n<br />Verifique a necessidade de uma nova aquisição."
					})
					
					send_mail(subject="Medicamento acabando - Lembremed",
						message = mensagem,
						html_message = mensagem,
						from_email=settings.EMAIL_HOST_USER,
						recipient_list=[estoque.morador.responsavel.email],
						fail_silently=True,  # Set to True to suppress exceptions
					)


		else:
			Estoque.objects.create(
				morador = Morador.objects.get(cpf=pcpf),
				medicamento = Medicamento.objects.get(codigo=pcodigo_medicamento),
				apresentacao = papresentacao,
				concentracao = pconcentracao,
				validade = pvalidade,
				prescricao = pprescricao,
				frequencia = pfrequencia,
				horarios = phorarios,
				qtd_disponivel = pqtd_disponivel,
			)


		# Após criar o usuário, atribua o papel associado

		return HttpResponse("medicamento salvo com sucesso")
	else:
		return HttpResponse("erro por GET no salvar")


@permission_required('lembremed.pode_medicar_morador')
def medicamento_excluir(request, pcpf, pcodigo):
	#Verifica se o estoque existe para o cpf
	estoque = Estoque.objects.get(codigo=pcodigo, morador__cpf=pcpf)
	if (estoque):
		#Exclui as administracoes deste estoque
		Administra.objects.filter(estoque=estoque).delete()

		#Exclui o estoque
		estoque.delete()

		return HttpResponse("Administração cadastrada com sucesso!")

	else:
		return HttpResponse("Erro ao localizar estoque")


@permission_required('lembremed.pode_medicar_morador')
def medicamento_administrar(request, pcpf, pcodigo):
	#Verifica se o estoque existe para o cpf
	estoque = Estoque.objects.get(codigo=pcodigo, morador__cpf=pcpf)
	if (estoque):
		#Atualiza o estoque
		estoque.qtd_disponivel -= estoque.prescricao / estoque.apresentacao.razao_prescricao_comercial
		estoque.save()

		#Registra a administracao
		Administra.objects.create(
			profissional = Profissional.objects.get(usuario=request.user),
			morador = estoque.morador,
			estoque = estoque,
			dthr_administracao = datetime.now(),
		)
		
		if (estoque.estimativa_duracao() <= 7):
			#Verifica se o responsavel tem telegram cadastrado
			if (estoque.morador.responsavel.telegram_id):
				url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
				dados_post = {
					'chat_id': estoque.morador.responsavel.telegram_id,
					'text': f"Medicamento {estoque.medicamento.principio} {estoque.apresentacao.unidade_prescricao} recém administrado tem 7 dias ou menos de estoque\nVerifique a necessidade de uma nova aquisição"
				}

				x = requests.post(url, json = dados_post)

				#requests.get(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage?chat_id={estoque.morador.responsavel.telegram_id}&text=Medicamento {estoque.medicamento.principio} {estoque.apresentacao.unidade_prescricao} recém administrado tem 7 dias ou menos de estoque")
			if (estoque.morador.responsavel.email):
				
				mensagem = render_to_string('email_templates/basic_email.html', {
						'title': "Medicamento acabando - Lembremed",
						'message': f"Olá {estoque.morador.responsavel.nome.split()[0]}." 
									f"\n<br />O medicamento {estoque.medicamento.principio} {estoque.apresentacao.unidade_prescricao} foi recém administrado agora tem 7 dias ou menos de estoque disponível."
									f"\n<br />Verifique a necessidade de uma nova aquisição."
				})
				
				send_mail(subject="Medicamento acabando - Lembremed",
					message = mensagem,
					html_message = mensagem,
					from_email=settings.EMAIL_HOST_USER,
					recipient_list=[estoque.morador.responsavel.email],
					fail_silently=True,  # Set to True to suppress exceptions
				)

		return HttpResponse("Administração cadastrada com sucesso!")

	else:
		return HttpResponse("Erro ao localizar estoque")
