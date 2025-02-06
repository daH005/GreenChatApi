from functools import wraps
from traceback import print_exc

from sqlalchemy.exc import DBAPIError

from config import DEFAULT_TRANSACTION_RETRY_MAX_ATTEMPTS
from db.builders import db_sync_builder

__all__ = (
    'transaction_retry_decorator',
)


def transaction_retry_decorator(max_attempts: int = DEFAULT_TRANSACTION_RETRY_MAX_ATTEMPTS):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, __cur_attempt: int = 0, **kwargs):
            try:
                return func(*args, **kwargs)
            except DBAPIError:
                print_exc()
                db_sync_builder.session.rollback()

                if __cur_attempt > max_attempts:
                    raise

                return wrapper(*args, **kwargs, __cur_attempt=__cur_attempt + 1)

        return wrapper
    return decorator
