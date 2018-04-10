"""
Usage:
    __main__.py

Options:
    -h --help
    --version   Show version.
"""
import os
import sys
import logging
from threading import Thread

from docopt import docopt
from telegram.ext import Filters
from telegram.ext import CommandHandler

from db import create_db_tables
from handlers.commands.alarm import set_timer, unset
from handlers.commands.commands import (
    btc, caps, ayuda, dolar, start, expense,
    get_questions, get_users, add_question,
    add_answer, cotizaciones, weather, code,
    subte, subte_novedades, remove_question,
    edit_question,
)
from handlers.messages.inline import code_markdown
from handlers.messages.unknown import unknown
from handlers.messages.message import (
    parse_msgs
)
from telegram_bot import TelegramBot

logger = logging.getLogger()

handler = logging.StreamHandler()
fh = logging.FileHandler('bot.log')

formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

COMMANDS = {
    'btc': btc,
    'caps': caps,
    'ayuda': ayuda,
    'dolar': dolar,
    'start': start,
    'users': get_users,
    'questions': get_questions,
    'gasto': expense,
    'add_question': add_question,
    'add_answer': add_answer,
    'edit_question': edit_question,
    'remove': remove_question,
    'cambio': cotizaciones,
    'clima': weather,
    'code': code,
    'subte': subte,
    'subtenews': subte_novedades,
}


def main():
    logger.info("Starting main...")

    message_handlers = [parse_msgs, ]

    bot = TelegramBot()
    bot.register_commands(COMMANDS)
    bot.register_message_handler(message_handlers)

    set_handler = bot.create_command_args(
        'set', set_timer, pass_args=True, pass_job_queue=True, pass_chat_data=True
    )
    bot.add_handler(set_handler)

    unset_handler = bot.create_command_args(
        'unset', unset, pass_args=False, pass_job_queue=False, pass_chat_data=True
    )
    bot.add_handler(unset_handler)

    code_handler = bot.create_inlinequery(code_markdown)
    bot.add_handler(code_handler)

    unknown_handler = bot.create_msg(unknown, Filters.command)
    bot.add_handler(unknown_handler)

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        bot.updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(bot, update):
        bot.update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    bot.add_handler(CommandHandler('r', restart, filters=Filters.user(username='@eduzen')))
    bot.start()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='eduzen_bot 1.0')
    try:
        if not os.path.exists('my_database.db'):
            create_db_tables()
        main()
    except Exception:
        logger.exception('bye bye')