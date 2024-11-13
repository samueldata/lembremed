    
import asyncio
from django.core.management import call_command

"""
async def MeuTelegramBot():
    call_command('run_tg_bot')
    return None
"""

def StartTGBot():
    call_command('run_tg_bot')
    return None