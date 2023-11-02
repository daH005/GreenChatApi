from os import environ
from dotenv import load_dotenv  # pip install python-dotenv
from typing import Final

__all__ = (
    'HOST',
)

load_dotenv()
HOST: Final[str] = environ.get('HOST', 'localhost')
