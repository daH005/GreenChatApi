from typing import Final
from redis import Redis  # pip install redis
from random import randint

from api.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_CODES_EXPIRES,
)

__all__ = (
    'app',
    'make_and_save_code',
    'code_is_valid',
    'delete_code',
)

app: Redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
_KEY_PREFIX: Final[str] = 'greenchat_mail_codes'


def make_and_save_code() -> int:
    code: int = randint(1000, 9999)
    key: str = _make_key(code)
    if app.exists(key):
        return make_and_save_code()
    app.set(key, code, ex=REDIS_CODES_EXPIRES)
    return code


def code_is_valid(code: int | str) -> bool:
    return bool(app.exists(_make_key(code)))


def delete_code(code: int | str) -> None:
    app.delete(_make_key(code))


def _make_key(code: int | str) -> str:
    return _KEY_PREFIX + str(code)
