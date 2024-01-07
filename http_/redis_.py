from typing import Final
from redis import Redis  # pip install redis
from random import randint

from api.config import REDIS_HOST, REDIS_PORT

__all__ = (
    'app',
    'make_and_save_code',
    'code_is_valid',
    'delete_code',
)

app: Redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
REDIS_SET_NAME: Final[str] = 'greenchat_mail_codes'


def make_and_save_code() -> int:
    code: int = randint(1000, 9999)
    if app.sismember(REDIS_SET_NAME, str(code)):
        return make_and_save_code()
    app.sadd(REDIS_SET_NAME, str(code))
    return code


def code_is_valid(code: int | str) -> bool:
    return bool(app.sismember(REDIS_SET_NAME, str(code)))


def delete_code(code: int | str) -> None:
    app.srem(REDIS_SET_NAME, str(code))
    