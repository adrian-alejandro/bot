"""
unknown - command
"""
import random

answers = (
    "https://media.giphy.com/media/3o7abL1nxw0AvOK1pu/giphy.gif",
    "https://media.giphy.com/media/a0FuPjiLZev4c/giphy.gif",
    "https://media.giphy.com/media/vQqeT3AYg8S5O/giphy.gif",
    "https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif",
    "https://media.giphy.com/media/QjrrSbYaqgi1q/giphy.gif",
)


def unknown(bot, update):
    bot.send_document(
        chat_id=update.message.chat_id, document=random.choice(answers)
    )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Mmmm, no sé si fuí claro, pero no te capto",
    )
