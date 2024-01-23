from typing import Final
from redis import Redis  # pip install redis
from random import randint

from api.hinting import raises
from api.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_CODES_EXPIRES,
    DEBUG,
    TEST_PASS_EMAIL_CODE,
)

__all__ = (
    'app',
    'make_and_save_code',
    'code_is_valid',
    'delete_code',
)

app: Redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
_KEY_PREFIX: Final[str] = 'greenchat_mail_codes'
_ENCODING: Final[str] = 'utf-8'


@raises(ValueError)
def make_and_save_code(identify: str) -> int:
    code: int = _make_random_code()
    key: str = _make_key(identify)
    if app.exists(key):
        raise ValueError
    app.set(key, code, ex=REDIS_CODES_EXPIRES)
    return code


def _make_random_code() -> int:
    return randint(1000, 9999)


def code_is_valid(identify: str,
                  code: int,
                  ) -> bool:
    if DEBUG and code == TEST_PASS_EMAIL_CODE:
        return True

    existed_code: bytes | None = app.get(_make_key(identify))
    if existed_code is not None:
        return existed_code.decode(_ENCODING) == str(code)
    return False


def delete_code(identify: str) -> None:
    app.delete(_make_key(identify))


def _make_key(identify: str) -> str:
    return _KEY_PREFIX + identify
