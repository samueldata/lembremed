from django.core.management.base import BaseCommand
from lembremed.utils import popular_tabela_com_csv

class Command(BaseCommand):
    help = 'Popula a tabela Medicamento com dados do arquivo CSV'

    def handle(self, *args, **kwargs):
        popular_tabela_com_csv()