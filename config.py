from os import environ
from dotenv import load_dotenv  # pip install python-dotenv
from typing import Final

__all__ = (
    'HOST',
    'PORT',
    'URL',
)

load_dotenv()
HOST: Final[str] = environ.get('HOST', 'localhost')
PORT: Final[int] = int(environ.get('PORT', 8070))
URL: Final[str] = f'ws://{HOST}:{PORT}'
