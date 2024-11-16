from django.core.management.base import BaseCommand
from lembremed.utils import rodar_tg_bot

class Command(BaseCommand):
	help = 'Popula a tabela Medicamento com dados do arquivo CSV'

	def handle(self, *args, **kwargs):
		rodar_tg_bot()