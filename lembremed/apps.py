from django.apps import AppConfig


class LembremedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lembremed'

    """
    def ready(self):
        from . import jobs
        import os
        import asyncio

        if os.environ.get('RUN_MAIN', None) != 'true':
            #jobs.StartTGBot()
            #A chamada desta funcao interrompe a execucao do script de inicializacao do Django
            print('\nIniciando o servidor\n\n')
    """
