from random import randint

from common.hinting import raises
from config.api import DEBUG, EMAIL_CODES_EXPIRES, EMAIL_PASS_CODE, EMAIL_CODES_MAX_ATTEMPTS
from http_.users.email.codes.exceptions import InvalidCodeException
from http_.users.email.codes.key_prefixes import KeyPrefix

__all__ = (
    'make_and_save_email_code',
    'email_code_is_valid',
    'delete_email_code',
)


@raises(InvalidCodeException)
def make_and_save_email_code(identify: str,
                             code: int | None = None,
                             ) -> int:
    if KeyPrefix.EMAIL_CODE.exists(identify):
        raise InvalidCodeException

    if code is None:
        code: int = _make_random_four_digit_number()

    KeyPrefix.EMAIL_CODE.set(identify, code, EMAIL_CODES_EXPIRES)
    KeyPrefix.EMAIL_CODE_COUNT.set(identify, 0)

    return code


def _make_random_four_digit_number() -> int:
    return randint(1000, 9999)


def email_code_is_valid(identify: str,
                        code: int,
                        ) -> bool:
    if DEBUG and code == EMAIL_PASS_CODE:
        return True

    if not KeyPrefix.EMAIL_CODE.exists(identify):
        return False

    try:
        cur_count: int = int(KeyPrefix.EMAIL_CODE_COUNT.get(identify))
    except ValueError:
        return False

    if cur_count > EMAIL_CODES_MAX_ATTEMPTS:
        delete_email_code(identify)
        return False

    KeyPrefix.EMAIL_CODE_COUNT.set(
        identify,
        cur_count + 1,
    )
    return KeyPrefix.EMAIL_CODE.get(identify) == str(code)


def delete_email_code(identify: str) -> None:
    KeyPrefix.EMAIL_CODE.delete(identify)
    KeyPrefix.EMAIL_CODE_COUNT.delete(identify)
