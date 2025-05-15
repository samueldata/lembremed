import csv
from .models import Medicamento, Responsavel
#from django.contrib.auth import get_user_model


import requests
import sys

def checkar_tg_bot():
	try:
		url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
		dados_post = {
			'chat_id': '5095250006', #Allan
			'text': f"Teste de funcionamento do telegram pelo alwaysdata.net"
		}

		response = requests.post(url, json = dados_post)

		# Check if the response status code is 200
		if response.status_code != 200:
			print(1)
			sys.exit(1)

		# Try to parse the response as JSON
		try:
			response_json = response.json()
		except ValueError:
			print(1)
			sys.exit(1)

		# Check if the specified attribute exists in the JSON response
		if response_json['ok'] == True:
			print(0)
			sys.exit(0)
		else:
			print(1)
			sys.exit(1)
	except requests.RequestException:
		print(1)
		sys.exit(1)


def popular_tabela_com_csv():
	#https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string
	with open('static/tabeladeremedios.csv', mode='r', encoding='utf-8-sig') as arquivo_csv:
		leitor_csv = csv.DictReader(arquivo_csv)
		for linha in leitor_csv:
			linha = {chave: valor for chave, valor in linha.items()}
			pprincipio = linha['principio']  # Substitua 'principio' pelo nome correto da coluna no arquivo CSV
			Medicamento.objects.create(principio=pprincipio)


from typing import Dict
from django.conf import settings
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
	Application,
	CommandHandler,
	ContextTypes,
	ConversationHandler,
	MessageHandler,
	filters,
	CallbackQueryHandler,
)


CADASTRADOS_ESCOLHENDO, DESCADASTRADOS_ESCOLHENDO = range(2)
DIGITANDO_CPF, DIGITANDO_NOME, DIGITANDO_LOGIN, DIGITANDO_SENHA = range(2, 6)

reply_keyboard_descadastrados = [
	["Cadastrar",],
	["Sair"],
]
reply_keyboard_cadastrados = [
	["Descadastrar", "Listar remédios",],
	["Sair"],
]
reply_keyboard = [
	[   InlineKeyboardButton("1", callback_data="1"),
		InlineKeyboardButton("2", callback_data="2"),
		InlineKeyboardButton("3", callback_data="3"), ],
	[   InlineKeyboardButton("4", callback_data="4"),
		InlineKeyboardButton("5", callback_data="5"),
		InlineKeyboardButton("6", callback_data="6"), ],
	[   InlineKeyboardButton("7", callback_data="7"),
		InlineKeyboardButton("8", callback_data="8"),
		InlineKeyboardButton("9", callback_data="9"), ],
	[   InlineKeyboardButton("<=", callback_data="<="),
		InlineKeyboardButton("0", callback_data="0"),
		InlineKeyboardButton("OK", callback_data="OK"), ],
]
reply_keyboard_confirmacao = [
	["Confirmar cadastro",],
	["Voltar"],
]
markup_descadastrados = ReplyKeyboardMarkup(reply_keyboard_descadastrados, one_time_keyboard=True)
markup_cadastrados = ReplyKeyboardMarkup(reply_keyboard_cadastrados, one_time_keyboard=True)
markup_teclado = InlineKeyboardMarkup(reply_keyboard)
markup_confirmacao = ReplyKeyboardMarkup(reply_keyboard_confirmacao, one_time_keyboard=True)


def rodar_tg_bot():
	"""Run the bot."""
	# Create the Application and pass it your bot's token.
	application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

	# Add conversation handler with the states CADASTRADOS_ESCOLHENDO, TYPING_CHOICE and TYPING_REPLY
	application.add_handler(MessageHandler(filters.ALL, mensagem_recebida))

	# Run the bot until the user presses Ctrl-C
	application.run_polling(allowed_updates=Update.ALL_TYPES)


async def mensagem_recebida(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	#Verifica se a mensagem recebida tem um hash valido
	text = update.message.text
	responsaveis = [responsavel async for responsavel in Responsavel.objects.filter(hashcode=text)]
	if (len(responsaveis) == 1):
		responsavel = responsaveis[0]
		responsavel.telegram_id = update.effective_user.id
		responsavel.hashcode = ''
		await responsavel.asave()
		await update.message.reply_text(
			"Cadastro atualizado com sucesso!"
		)

	else:
		await update.message.reply_text(
			"Desculpe, não consegui encontrar o responsável..."
		)








"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	ja_entrou = context.user_data.get("ja_entrou", None)

	#Verifica se o usuario jah esta cadastrado no servico
	#responsavel = Responsavel.objects.filter(telegram_id=update.effective_user.id)

	#Verifica se a pessoa eh cadastrada
	responsaveis = [responsavel async for responsavel in Responsavel.objects.filter(telegram_id=update.effective_user.id)]
	if (len(responsaveis) == 1):
		responsavel = responsaveis[0]
		#Verifica se nao eh o primeiro acesso da pessoa
		if ja_entrou:
			await update.message.reply_text(
				"Por favor, escolha uma opção",
				reply_markup=markup_cadastrados,
			)
		else:
			context.user_data["ja_entrou"] = True
			await update.message.reply_text(
				f"Olá {responsavel.nome.split()[0]}! Eu sou o bot da LembreMed.\n"
				"Por favor escolha uma das opções",
				reply_markup=markup_cadastrados,
			)

		return CADASTRADOS_ESCOLHENDO

	else:
		#Verificar se estah mandando um hash de bind com o usuario do banco
		if (False):
			pass
		else:
			#Verifica se nao eh o primeiro acesso da pessoa
			if ja_entrou:
				await update.message.reply_text(
					"Olá! Eu sou o bot da LembreMed. "
					"Por favor escolha uma das opções",
					reply_markup=markup_descadastrados,
				)
			else:
				context.user_data["ja_entrou"] = True
				await update.message.reply_text(
					"Por favor, escolha uma opção",
					reply_markup=markup_descadastrados,
				)

			return DESCADASTRADOS_ESCOLHENDO


async def opcao_descadastrados(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	text = update.message.text

	if (text == 'Cadastrar'):
		await update.message.reply_text(
			"Vamos iniciar o cadastro.\nDigite seu cpf"
		)

		return DIGITANDO_CPF


async def receber_cpf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	#Verifica se o cpf eh numericamente valido
	text = update.message.text
	if (text != ""):
		context.user_data["cpf"] = text
		await update.message.reply_text(
			'Agora digite seu nome.'
		)

		return DIGITANDO_NOME

	else:
		await update.message.reply_text(
			'CPF inválido. Digite novamente.'
		)

		return DIGITANDO_CPF



async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	text = update.message.text
	if (text != ""):
		context.user_data["nome"] = text
		await update.message.reply_text(
			'Ok.\nAgora digite seu e-mail',
		)

		return DIGITANDO_LOGIN


async def receber_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	#Verifica se o email eh valido
	text = update.message.text
	if (text != ""):
		context.user_data["login"] = text
		await update.message.reply_text(
			'Agora digite a senha no teclado\n\nClique em [OK] para verificar a senha e clique novemente para confirmar a senha',
			reply_markup=markup_teclado
		)

		return DIGITANDO_SENHA

	else:
		await update.message.reply_text(
			'E-mail inválido. Digite novamente.'
		)

		return DIGITANDO_LOGIN


async def apertar_botao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	query = update.callback_query
	data = query.data

	if data == "OK":
		# Process the selected number (stored in context.user_data)
		typed_pass = context.user_data.get("typed_pass", None)
		if typed_pass:
			confirm = context.user_data.get("confirmed_password", None)
			if confirm:
				context.user_data["senha"] = context.user_data["typed_pass"]
				del context.user_data["typed_pass"]

				await query.answer("Senha salva!")
				await context.bot.send_message(
					chat_id=query.message.chat_id,
					text="Confirme as informações:\n"
						f"CPF: {context.user_data["cpf"]}\n"
						f"Nome: {context.user_data["nome"]}\n"
						f"E-mail: {context.user_data["login"]}\n"
						f"Senha: {context.user_data["senha"]}",
					reply_markup=markup_confirmacao
				)

			else:
				context.user_data["confirmed_password"] = True
				await query.answer(f"Sua senha é [{typed_pass}] Aperte [OK] novamente para confirmar")
		else:
			await query.answer("Digite uma senha!")

	elif data == "<=":
		# Apagando o ultimo caractere digitado
		typed_pass = context.user_data.get("typed_pass", None)
		if typed_pass:
			confirm = context.user_data.get("confirmed_password", None)
			if confirm:
				context.user_data["senha"] = context.user_data["typed_pass"]
				del context.user_data["typed_pass"]

				await query.answer("Senha salva!")
				await context.bot.send_message(
					chat_id=query.message.chat_id,
					text="Confirme as informações:\n"
						f"CPF: {context.user_data["cpf"]}\n"
						f"Nome: {context.user_data["nome"]}\n"
						f"E-mail: {context.user_data["login"]}\n"
						f"Senha: {context.user_data["senha"]}",
					reply_markup=markup_confirmacao
				)

			else:
				context.user_data["confirmed_password"] = True
				await query.answer(f"Sua senha é [{typed_pass}] Aperte [OK] novamente para confirmar")
		else:
			await query.answer("Digite uma senha!")
	else:
		try:
			context.user_data["typed_pass"] += data
		except:
			context.user_data["typed_pass"] = data
		finally:
			await query.answer()


async def receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	text = update.message.text

	if (text == 'Confirmar cadastro'):
		usuario = await User.objects.acreate(username=context.user_data["cpf"], email=context.user_data["login"], password=context.user_data["senha"])
		await usuario.asave()
		await Responsavel.objects.acreate(cpf=context.user_data["cpf"], telegram_id=update.effective_user.id, nome=context.user_data["nome"], usuario=usuario)

		await update.message.reply_text(
			'Cadastro efetuado com sucesso.'
		)

	else:
		await update.message.reply_text(
			'Vamos começar novamente.'
		)

	return await start(update, context)


async def opcao_cadastrados(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	text = update.message.text

	if (text == "Listar remédios"):
		await update.message.reply_text(
			"Aqui está a lista dos seus remédios:"
			"\n-aaa"
			"\n-BBB"
		)
		return await start(update, context)

	else: #Descadastrar
		responsavel = await Responsavel.objects.aget(telegram_id=update.effective_user.id)
		await responsavel.adelete()

		await update.message.reply_text(
			"Você foi descadastrado com sucesso."
		)
		return await sair(update, context)


async def mensagem_estranha(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text(
		"Nao entendi sua mensagem",
	)

	await start(update, context)


async def sair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	try:
		context.user_data["ja_entrou"] = False
	except:
		pass

	await update.message.reply_text(
		"Até mais!",
	)
	return ConversationHandler.END

"""
