from random import choice
from string import ascii_uppercase
from datetime import datetime

__all__ = (
    'COMMON_DATETIME',
    'make_random_string',
)

COMMON_DATETIME: datetime = datetime(
    year=2024, month=10, day=10,
)


def make_random_string(n: int = 40) -> str:
    """Генерирует случайную n-символьную строку."""
    return ''.join(choice(ascii_uppercase) for _ in range(n))
