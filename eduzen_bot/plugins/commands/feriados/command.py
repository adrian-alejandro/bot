"""
feriados - feriadosarg
"""
import pytz
import structlog
from datetime import datetime

from api import get_feriados, prettify_feriados, filter_feriados

logger = structlog.get_logger(filename=__name__)


def feriadosarg(bot, update, *args, **kwargs):
    today = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
    feriados = get_feriados(today.year)
    if not feriados:
        update.message.reply_text('🏳️ La api de feriados no responde')
        return

    following_feriados = filter_feriados(today, feriados)
    if following_feriados:
        msg = prettify_feriados(today, following_feriados)
    else:
        msg = 'No hay más feriados este año'

    update.message.reply_text(msg, parse_mode='markdown')
