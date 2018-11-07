import structlog
import tmdbsimple as tmdb

from eduzen_bot.keys import TMDB
from eduzen_bot.plugins.commands.movies.api import get_yts_torrent_info, get_yt_trailer


logger = structlog.get_logger(filename=__name__)

IMDB_LINK = 'https://www.imdb.com/title/{}'
YT_LINK = 'https://www.youtube.com/watch?v={}'
tmdb.API_KEY = TMDB["API_KEY"]


def get_movie_imdb(bot, update, **context):
    imdb_id = context['data']['movie']['imdb_id']
    answer = f"[IMDB]({IMDB_LINK.format(imdb_id)}"

    bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=answer,
        parse_mode='markdown'
    )


def get_movie_youtube(bot, update, **context):
    movie = context['data']['movie']
    answer = f"[Trailer]({get_yt_trailer(movie['videos'])})"
    bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=answer,
        parse_mode='markdown'
    )


def get_movie_torrent(bot, update, **context):
    movie = context['data']['movie']
    torrent = get_yts_torrent_info(movie['imdb_id'])
    if torrent:
        url, seeds, size, quality = torrent
        answer = (
            f"🏴‍☠️ [{movie['title']}]({url})\n\n"
            f"🌱 Seeds: {seeds}\n\n"
            f"🗳 Size: {size}\n\n"
            f"🖥 Quality: {quality}"
        )
    else:
        answer = "🚧 No torrent available for this movie."

    bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=answer,
        parse_mode='markdown'
    )
