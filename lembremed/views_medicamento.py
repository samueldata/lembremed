from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.db.models import Q
from lembremed.models import Estoque, Horario, Medicamento, Administra, Morador, Profissional, Apresentacao, Instituicao, HORA_CHOICES, Saida
from lembremed.decorators import adiciona_contexto
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from datetime import datetime, timedelta, time
from django.core.mail import send_mail
from django.db import transaction
import re
from decimal import Decimal
import requests
from django.conf import settings
import traceback

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
	#Verifica se tem os tipos de apresentacao dos medicamentos cadastrados
	verificar_apresentacoes()

	print('foi')

	#Verifica se eh profissional ou instituicao cadastrando
	if (isinstance(contexto_padrao['usuario'], Instituicao)):
		morador = Morador.objects.filter(cpf=pcpf, instituicao=contexto_padrao['usuario']).first()

	elif(isinstance(contexto_padrao['usuario'], Profissional)):
		morador = Morador.objects.filter(cpf=pcpf, instituicao=contexto_padrao['usuario'].instituicao).first()

	estoques = Estoque.objects.filter(morador=morador)
	saidas = Saida.objects.filter(morador=morador)
	print('\n\n\n\n')
	from pprint import pprint
	pprint(saidas)

	print('\n\n')
	lista_estoques = []
	for estoque in estoques:
		ultima_administracao = Administra.objects.filter(estoque=estoque, aplicado=True).order_by('-dthr_administracao').first()
		lista_estoques.append({ #Cria o objeto com o estoque e sua ultima administracao
			'estoque': estoque,
			'ultima_administracao': ultima_administracao,
			'duracao': estoque.estimativa_duracao(),
			'horarios': '  / '.join([HORA_CHOICES[h.hora][1] for h in estoque.horarios.all()]),
		})

	context = {
		'lista_estoques': lista_estoques, 'morador': morador,
		'tem_saida_aberta': any(s.dt_fim is None for s in saidas),
		}

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
		'HORA_CHOICES': HORA_CHOICES,
		'horarios_selecionados': [h.hora for h in estoque.horarios.all()],
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
		'HORA_CHOICES': HORA_CHOICES,
		'horarios_selecionados': [],
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
		pcontinuo = True if request.POST.get('continuo') == 'S' else False
		pdias_uso = int(request.POST.get('dias_uso')) if pcontinuo == False else None
		phorarios = request.POST.getlist('hora')
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
			estoque.continuo = pcontinuo
			estoque.dias_uso = pdias_uso
			estoque.dthr_alteracao = timezone.localtime(timezone.now())
			pqtd_alterar = re.findall(r'^(\+|\-)(\d+|\d+\.\d+)$', pqtd_alterar)

			if (len(pqtd_alterar) == 1):
				psinal, pqtd_alterar = pqtd_alterar[0]
				estoque.qtd_disponivel = estoque.qtd_disponivel if estoque.qtd_disponivel else Decimal('0')
				if (psinal == '+'):
					estoque.qtd_disponivel += Decimal(pqtd_alterar)
				else:
					estoque.qtd_disponivel -= Decimal(pqtd_alterar)
			estoque.save()

			estoque.horarios.all().delete()
			for h in phorarios:
				Horario.objects.create(estoque=estoque, hora=int(h))

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
						from_email = settings.EMAIL_HOST_USER,
						recipient_list = [estoque.morador.responsavel.email],
						fail_silently = True,  # Set to True to suppress exceptions
					)


		else:
			estoque = Estoque.objects.create(
				morador = Morador.objects.get(cpf=pcpf),
				medicamento = Medicamento.objects.get(codigo=pcodigo_medicamento),
				apresentacao = papresentacao,
				concentracao = pconcentracao,
				validade = pvalidade,
				prescricao = pprescricao,
				frequencia = pfrequencia,
				continuo = pcontinuo,
				dias_uso = pdias_uso,
				dthr_alteracao = timezone.localtime(timezone.now()),
				qtd_disponivel = pqtd_disponivel,
			)

			for h in phorarios:
				Horario.objects.create(estoque=estoque, hora=int(h))

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
	estoque = Estoque.objects.get(codigo=pcodigo, morador__cpf=pcpf)

	# Pega o início (00:00:00) e o fim (23:59:59.999999) do dia de hoje no fuso horário local
	agora_local = timezone.localtime(timezone.now())
	inicio_do_dia_local = agora_local.replace(hour=0, minute=0, second=0, microsecond=0)
	fim_do_dia_local = agora_local.replace(hour=23, minute=59, second=59, microsecond=999999)

	# Agora fazemos o filtro em UTC (que é o formato salvo no banco) pois o Django armazena em UTC e está ciente do TIME_ZONE
	arr_administracoes = Administra.objects.filter(
		Q(dthr_administracao__gte=inicio_do_dia_local) & Q(dthr_administracao__lte=fim_do_dia_local),
		estoque = estoque
	)

	horarios_administrados = [a.horario for a in arr_administracoes]
	horarios_prescricao = [h for h in estoque.horarios.all()]
	disponiveis = [h.hora for h in horarios_prescricao if h not in horarios_administrados]



	from pprint import pprint
	print('\n\n\n\n\n\n\n\n\n')
	print('inico')
	pprint(inicio_do_dia_local)
	print('fim')
	pprint(fim_do_dia_local)
	print('\n\n\n')
	print('datas do banco')
	pprint(arr_administracoes[0].dthr_administracao if len(arr_administracoes) > 0 else None)
	pprint(arr_administracoes[1].dthr_administracao if len(arr_administracoes) > 1 else None)
	pprint(arr_administracoes[2].dthr_administracao if len(arr_administracoes) > 2 else None)
	pprint(arr_administracoes[3].dthr_administracao if len(arr_administracoes) > 3 else None)
	pprint(arr_administracoes[4].dthr_administracao if len(arr_administracoes) > 4 else None)
	pprint(arr_administracoes[5].dthr_administracao if len(arr_administracoes) > 5 else None)
	pprint(arr_administracoes[6].dthr_administracao if len(arr_administracoes) > 6 else None)
	pprint(arr_administracoes[7].dthr_administracao if len(arr_administracoes) > 7 else None)
	pprint(arr_administracoes[8].dthr_administracao if len(arr_administracoes) > 8 else None)
	print('\n\n\n')



	context = {
		'estoque': estoque,
		'disponiveis': disponiveis,
		'HORA_CHOICES': HORA_CHOICES,
		}
	return render(request, 'medicamento/administrar.html', context)

@permission_required('lembremed.pode_medicar_morador')
def medicamento_salvar_administracao(request, pcpf, pcodigo):
	#Verifica se o estoque existe para o cpf
	estoque = Estoque.objects.get(codigo=pcodigo, morador__cpf=pcpf)
	if (estoque):
		try:
			# Inicia o transaction com o banco
			with transaction.atomic():
				phora = request.POST.get('hora')
				horario = Horario.objects.get(estoque=estoque, hora=int(phora))
				hoje = timezone.localtime(timezone.now()).date()

				###############################################################
				# Marca os horarios anteriores sem administracao como nao aplicados, caso existam
				limite = estoque.dthr_alteracao.date()
				ultima_saida = Saida.objects.filter(morador=estoque.morador).order_by('-dt_inicio').first()
				if ultima_saida:
					limite = max(estoque.dthr_alteracao, 
						ultima_saida.dt_fim,
					)

				#limite = timezone.make_aware(limite, timezone.get_current_timezone())  # Converte para um datetime "aware"
				horarios = estoque.horarios.all()
				
				while limite <= hoje:

					print('\n\n\n\n')
					print(limite)

					for horario_i in horarios:
						if limite < hoje or horario_i.hora < horario.hora:
							# Verifica se já existe uma administração nesse horário nesta data
							existe = Administra.objects.filter(
								morador=estoque.morador,
								estoque=estoque,
								horario=horario_i,
								dthr_administracao__date=limite
							).exists()

							if not existe:
								#Marca o horario como nao administrado
								Administra.objects.create(
									profissional = Profissional.objects.get(usuario=request.user),
									morador = estoque.morador,
									estoque = estoque,
									dthr_administracao = datetime.combine(limite, time(horario_i.hora)),
									horario = horario_i,
									aplicado = False
								)

					limite += timedelta(days=1)

					
				#Atualiza o estoque
				estoque.qtd_disponivel -= estoque.prescricao / estoque.apresentacao.razao_prescricao_comercial
				estoque.save()

				#Registra a administracao
				Administra.objects.create(
					profissional = Profissional.objects.get(usuario=request.user),
					morador = estoque.morador,
					estoque = estoque,
					dthr_administracao = timezone.localtime(timezone.now()),
					horario = horario,
					aplicado = True
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

		except Exception as e:
			# rollback automático
			print("Erro:", e,)
			traceback.print_exc()  # This will print the traceback to the console
			return HttpResponse("Erro interno", status=500)

	else:
		return HttpResponse("Erro ao localizar estoque")
