import os
from functools import partial
import pkgutil
import structlog

from telegram.ext import (
    CommandHandler, MessageHandler, Filters, InlineQueryHandler, Updater
)
from telegram.error import (
    TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
)
from keys import TOKEN, EDUZEN_ID

logger = structlog.get_logger(filename=__name__)

here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

FILTERS = {
    'command': Filters.command,
    'text': Filters.text,
}


class TelegramBot(object):
    """Just a class for python-telegram-bot"""

    def __init__(self, workers=4):
        self.updater = Updater(token=TOKEN, workers=workers)
        logger.info("Created updater for %s" % (self.updater.bot.name))
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_error_handler(self.error)
        self._load_plugins()

    def start(self):
        self.updater.start_polling()
        self.send_msg_to_eduzen("eduzen_bot reiniciado!")
        self.updater.idle()

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        try:
            raise error

        except Unauthorized:
            # remove update.message.chat_id from conversation list
            logger.error("Update caused Unauthorized error")
        except BadRequest:
            # handle malformed requests - read more below!
            logger.error('Update "%s" caused error "%s"', (update, error))
        except TimedOut:
            # handle slow connection problems
            logger.warning('Update "%s" caused TimedOut "%s"', (update, error))
        except NetworkError:
            # handle other connection problems
            logger.error('Update "%s" caused error "%s"', (update, error))
        except ChatMigrated as e:
            # the chat_id of a group has changed, use e.new_chat_id instead
            logger.error('Update "%s" caused error "%s"', (update, error))
        except TelegramError:
            # handle all other telegram related errors
            logger.error('Update "%s" caused error "%s"', (update, error))
        except Exception:
            logger.exception('Update "%s" caused error "%s"', (update, error))

    def add_handler(self, handler):
        self.dispatcher.add_handler(handler)

    def add_list_of_handlers(self, handlers):
        for handler in handlers:
            self.add_handler(handler)

    def send_msg_to_eduzen(self, msg):
        logger.info("aviso a eduzen")
        self.updater.bot.send_message(EDUZEN_ID, msg)

    def create_command(self, name, func):
        return CommandHandler(name, func, pass_args=True)

    def create_command_args(
        self, name, func, pass_args=True, pass_job_queue=True, pass_chat_data=True
    ):
        return CommandHandler(
            name,
            func,
            pass_args=pass_args,
            pass_job_queue=pass_job_queue,
            pass_chat_data=pass_chat_data,
        )

    def create_inlinequery(self, func):
        return InlineQueryHandler(func)

    def create_list_of_commands(self, kwargs):
        return [self.create_command(key, value) for key, value in kwargs.items()]

    def create_msg(self, func, filters=Filters.text):
        return MessageHandler(filters, func)

    def create_list_of_msg_handlers(self, args):
        return [self.create_msg(value) for value in args]

    def register_commands(self, kwargs):
        commands = self.create_list_of_commands(kwargs)
        self.add_list_of_handlers(commands)

    def register_message_handler(self, args):
        msgs = self.create_list_of_msg_handlers(args)
        self.add_list_of_handlers(msgs)

    def _get_commands(self, plugin):
        plugins = {}
        for line in plugin.__doc__.strip().splitlines():
            command = [substring.strip() for substring in line.strip().split("-")]
            plugins[command[0]] = getattr(plugin, command[1])
        return plugins

    def _get_cmd_plugins(self):
        plugins = {}
        plugins_path = get_path("plugins/commands")
        for importer, package_name, _ in pkgutil.iter_modules([plugins_path]):
            logger.info(f"Loading {package_name}...")
            sub_modules = get_path(plugins_path, package_name)
            importer.find_module(package_name).load_module(package_name)
            for importer, package_name, _ in pkgutil.iter_modules([sub_modules]):
                plugin = importer.find_module(package_name).load_module(package_name)
                if not plugin.__doc__:
                    continue

                plugins.update(self._get_commands(plugin))

        return plugins

    def _get_msg_plugins(self):
        plugins_path = get_path("plugins/messages")
        for importer, package_name, _ in pkgutil.iter_modules([plugins_path]):
            logger.info(f"Loading {package_name}...")
            sub_modules = get_path(plugins_path, package_name)
            importer.find_module(package_name).load_module(package_name)
            for importer, package_name, _ in pkgutil.iter_modules([sub_modules]):
                plugin = importer.find_module(package_name).load_module(package_name)
                if not plugin.__doc__:
                    continue

                for line in plugin.__doc__.strip().splitlines():
                    command = [substring.strip() for substring in line.strip().split("-")]
                    func = getattr(plugin, command[0])
                    flt = FILTERS.get(command[1])
                    cmd = self.create_msg(func, filters=flt)
                    self.add_handler(cmd)

    def _load_plugins(self):
        logger.info("Loading plugins...")
        plugins = self._get_cmd_plugins()
        self.register_commands(plugins)
        self._get_msg_plugins()
