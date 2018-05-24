"""
parse_msgs - text
"""
import os

from structlog import get_logger
from telegram import ChatAction
from telegram.ext.dispatcher import run_async

from autil import record_msg, parse_chat, get_or_create_user, prepare_text, parse_regular_chat

os.environ["NLTK_DATA"] = os.getcwd() + "/nltk_data"
from textblob import TextBlob


logger = get_logger(filename=__name__)


def parse_msgs(bot, update):
    import pdb; pdb.set_trace()
    username = update.message.from_user.username
    chat_id = update.message.chat_id

    logger.info("Parse_msgs... by %s", username)

    record_msg(update.message.from_user.name, update.message.text, chat_id=chat_id)
    get_or_create_user(update.message.from_user)

    text = prepare_text(update.message.text)
    blob = TextBlob(text)

    entities = update.message.parse_entities()
    if not entities:
        answer, gif = parse_regular_chat(blob)
        if answer:
            bot.send_chat_action(
                chat_id=update.message.chat_id, action=ChatAction.TYPING
            )
        if answer and not gif:
            bot.send_message(chat_id=update.message.chat_id, text=answer)
        elif answer and gif:
            bot.send_document(chat_id=update.message.chat_id, document=answer)
        return

    mentions = [
        value
        for key, value in entities.items()
        if "@eduzen_bot" in value or "@eduzenbot" in value
    ]
    if not mentions:
        return

    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    answer = parse_chat(blob)

    bot.send_message(chat_id=update.message.chat_id, text=answer)
