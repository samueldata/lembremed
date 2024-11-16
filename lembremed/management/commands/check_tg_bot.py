from django.core.management.base import BaseCommand
from lembremed.utils import checkar_tg_bot

class Command(BaseCommand):
	help = 'Popula a tabela Medicamento com dados do arquivo CSV'

	def handle(self, *args, **kwargs):
		checkar_tg_bot()