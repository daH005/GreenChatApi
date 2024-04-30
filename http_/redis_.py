from redis import Redis  # pip install redis
from random import randint
from enum import StrEnum

from api.hinting import raises
from api.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_CODES_EXPIRES,
    DEBUG,
    TEST_PASS_EMAIL_CODE,
    MAX_ATTEMPTS_TO_CHECK_EMAIL_CODE,
)

__all__ = (
    'app',
    'make_and_save_code',
    'code_is_valid',
    'delete_code',
)

app: Redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)


class KeyPrefix(StrEnum):
    EMAIL_CODE = 'greenchat_email_code_'
    EMAIL_CODE_COUNT = 'greenchat_email_code_count_'

    def get(self, identify: str) -> str:
        return app.get(self + identify)

    def set(self, identify: str,
            value: str | int,
            expires: float | None = None,
            ) -> None:
        app.set(self + identify, value, ex=expires)

    def delete(self, identify: str) -> None:
        app.delete(self + identify)

    def exists(self, identify: str) -> bool:
        return app.exists(self + identify)


@raises(ValueError)
def make_and_save_code(identify: str) -> int:
    if KeyPrefix.EMAIL_CODE.exists(identify):
        raise ValueError

    code: int = _make_random_code()
    KeyPrefix.EMAIL_CODE.set(identify, code, REDIS_CODES_EXPIRES)
    KeyPrefix.EMAIL_CODE_COUNT.set(identify, 0)

    return code


def _make_random_code() -> int:
    return randint(1000, 9999)


def code_is_valid(identify: str,
                  code: int,
                  ) -> bool:
    if DEBUG and code == TEST_PASS_EMAIL_CODE:
        return True

    if not KeyPrefix.EMAIL_CODE.exists(identify):
        return False

    try:
        cur_count: int = int(KeyPrefix.EMAIL_CODE_COUNT.get(identify))
    except ValueError:
        return False

    if cur_count > MAX_ATTEMPTS_TO_CHECK_EMAIL_CODE:
        delete_code(identify)
        return False

    KeyPrefix.EMAIL_CODE_COUNT.set(
        identify,
        cur_count + 1,
    )
    return KeyPrefix.EMAIL_CODE.get(identify) == str(code)


def delete_code(identify: str) -> None:
    KeyPrefix.EMAIL_CODE.delete(identify)
    KeyPrefix.EMAIL_CODE_COUNT.delete(identify)
