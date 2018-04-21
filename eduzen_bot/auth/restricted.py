import logging
from functools import wraps

LIST_OF_ADMINS = ("3652654",)

logger = logging.getLogger(__name__)


def restricted(func):

    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            logger.warning(f"Unauthorized access denied for {user_id}.")
            return

        return func(bot, update, *args, **kwargs)

    return wrapped