from os import environ
from dotenv import load_dotenv
from typing import Final
from pathlib import Path
from sqlalchemy.engine.url import URL

__all__ = (
    'BASE_DIR',
    'STATIC_FOLDER',
    'MEDIA_FOLDER',
    'DEBUG',
    'HOST',
    'HTTP_PORT',
    'WEBSOCKET_PORT',
    'CORS_ORIGINS',
    'JWT_SECRET_KEY',
    'JWT_ALGORITHM',
    'JWT_ACCESS_TOKEN_EXPIRES',
    'JWT_REFRESH_TOKEN_EXPIRES',
    'DB_URL',
    'REDIS_HOST',
    'REDIS_PORT',
    'REDIS_URL',
    'SMTP_HOST',
    'SMTP_PORT',
    'EMAIL',
    'EMAIL_PASSWORD',
    'EMAIL_CODES_EXPIRES',
    'EMAIL_PASS_CODE',
    'EMAIL_CODES_MAX_ATTEMPTS',
)

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent  # '.../api'
STATIC_FOLDER: Path = BASE_DIR.joinpath('static')
MEDIA_FOLDER: Path = BASE_DIR.joinpath('media')

DEBUG: Final[bool] = False if environ['DEBUG'].lower() == 'false' else bool(environ['DEBUG'])

HOST: Final[str] = environ['HOST']  # Хост общий для HTTP и WebSocket.
HTTP_PORT: Final[int] = int(environ['HTTP_PORT'])
WEBSOCKET_PORT: Final[int] = int(environ['WEBSOCKET_PORT'])

CORS_ORIGINS: Final[list[str]] = environ['CORS_ORIGINS'].split(',')

JWT_SECRET_KEY: Final[str] = environ['JWT_SECRET_KEY']
JWT_ALGORITHM: Final[str] = environ['JWT_ALGORITHM']
JWT_ACCESS_TOKEN_EXPIRES: Final[int] = int(environ['JWT_ACCESS_TOKEN_EXPIRES'])
JWT_REFRESH_TOKEN_EXPIRES: Final[int] = int(environ['JWT_REFRESH_TOKEN_EXPIRES'])

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

SMTP_HOST: Final[str] = environ['SMTP_HOST']
SMTP_PORT: Final[int] = int(environ['SMTP_PORT'])

EMAIL: Final[str] = environ['EMAIL']
EMAIL_PASSWORD: Final[str] = environ['EMAIL_PASSWORD']
EMAIL_CODES_EXPIRES: Final[int] = int(environ['EMAIL_CODES_EXPIRES'])
EMAIL_PASS_CODE: Final[int] = int(environ['EMAIL_PASS_CODE'])
EMAIL_CODES_MAX_ATTEMPTS: Final[int] = int(environ['EMAIL_CODES_MAX_ATTEMPTS'])
