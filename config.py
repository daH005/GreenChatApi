from os import environ
from dotenv import load_dotenv  # pip install python-dotenv
from typing import Final
from pathlib import Path
from sqlalchemy.engine.url import URL

__all__ = (
    'BASE_DIR',
    'DEBUG',
    'HOST',
    'HTTP_PORT',
    'WEBSOCKET_PORT',
    'CORS_ORIGINS',
    'JWT_SECRET_KEY',
    'JWT_ALGORITHM',
    'JWT_ACCESS_TOKEN_EXPIRES',
    'DB_URL',
    'REDIS_HOST',
    'REDIS_PORT',
    'REDIS_URL',
    'REDIS_CODES_EXPIRES',
    'SMTP_HOST',
    'SMTP_PORT',
    'EMAIL',
    'EMAIL_PASSWORD',
    'TEST_PASS_EMAIL_CODE',
    'MAX_ATTEMPTS_TO_CHECK_CODE',
)

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent  # '.../api'

DEBUG: Final[bool] = False if environ['DEBUG'].lower() == 'false' else bool(environ['DEBUG'])

HOST: Final[str] = environ['HOST']  # Хост общий для HTTP и WebSocket.
HTTP_PORT: Final[int] = int(environ['HTTP_PORT'])
WEBSOCKET_PORT: Final[int] = int(environ['WEBSOCKET_PORT'])

CORS_ORIGINS: Final[list[str]] = environ['CORS_ORIGINS'].split(',')

JWT_SECRET_KEY: Final[str] = environ['JWT_SECRET_KEY']
JWT_ALGORITHM: Final[str] = environ['JWT_ALGORITHM']
JWT_ACCESS_TOKEN_EXPIRES: Final[int] = int(environ['JWT_ACCESS_TOKEN_EXPIRES'])  # Секунды.

DB_URL: URL = URL.create(
    drivername=environ['DB_DRIVERNAME'],
    username=environ['DB_USERNAME'],
    password=environ['DB_PASSWORD'],
    host=environ['DB_HOST'],
    port=int(environ['DB_PORT']),
    database=environ['DB_NAME'],
)

REDIS_HOST: Final[str] = environ['REDIS_HOST']
REDIS_PORT: Final[int] = int(environ['REDIS_PORT'])
REDIS_URL: Final[str] = f'redis://{REDIS_HOST}:{REDIS_PORT}'
REDIS_CODES_EXPIRES: Final[int] = int(environ['REDIS_CODES_EXPIRES'])

SMTP_HOST: Final[str] = environ['SMTP_HOST']
SMTP_PORT: Final[int] = int(environ['SMTP_PORT'])

EMAIL: Final[str] = environ['EMAIL']
EMAIL_PASSWORD: Final[str] = environ['EMAIL_PASSWORD']
TEST_PASS_EMAIL_CODE: Final[int] = int(environ['TEST_PASS_EMAIL_CODE'])
MAX_ATTEMPTS_TO_CHECK_EMAIL_CODE: Final[int] = int(environ['MAX_ATTEMPTS_TO_CHECK_EMAIL_CODE'])

if __name__ == '__main__':
    print(BASE_DIR)
    print(DB_URL)
    print(CORS_ORIGINS)
    print(JWT_SECRET_KEY)
    print(DEBUG)
