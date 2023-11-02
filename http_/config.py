from os import environ
from typing import Final

from api.config import HOST

__all__ = (
    'HOST',
    'PORT',
)

PORT: Final[int] = int(environ.get('HTTP_PORT', 81))
