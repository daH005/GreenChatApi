from random import choice
from string import ascii_uppercase

__all__ = (
    'make_random_string',
)


def make_random_string(n: int = 40) -> str:
    """Генерирует случайную n-символьную строку."""
    return ''.join(choice(ascii_uppercase) for _ in range(n))
