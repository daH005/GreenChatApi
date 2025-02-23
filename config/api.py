from os import environ
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()

__all__ = (
    'DEBUG',

    'HOST',
    'HTTP_PORT',
    'WEBSOCKET_PORT',

    'SSL_CERTFILE',
    'SSL_KEYFILE',

    'CORS_ORIGINS',

    'JWT_SECRET_KEY',
    'JWT_ALGORITHM',
    'JWT_ACCESS_TOKEN_EXPIRES',
    'JWT_REFRESH_TOKEN_EXPIRES',

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

    'USER_AVATAR_MAX_CONTENT_LENGTH',
    'USER_BACKGROUND_MAX_CONTENT_LENGTH',
    'MESSAGE_FILES_MAX_CONTENT_LENGTH',
)

DEBUG: Final[bool] = False if environ['DEBUG'].lower() == 'false' else bool(environ['DEBUG'])

HOST: Final[str] = environ['HOST']  # Is common for HTTP and WebSocket.
HTTP_PORT: Final[int] = int(environ['HTTP_PORT'])
WEBSOCKET_PORT: Final[int] = int(environ['WEBSOCKET_PORT'])

SSL_CERTFILE: Final[Path] = Path(environ['SSL_CERTFILE'])
SSL_KEYFILE: Final[Path] = Path(environ['SSL_KEYFILE'])

CORS_ORIGINS: Final[list[str]] = environ['CORS_ORIGINS'].split(',')

JWT_SECRET_KEY: Final[str] = environ['JWT_SECRET_KEY']
JWT_ALGORITHM: Final[str] = environ['JWT_ALGORITHM']
JWT_ACCESS_TOKEN_EXPIRES: Final[int] = int(environ['JWT_ACCESS_TOKEN_EXPIRES'])
JWT_REFRESH_TOKEN_EXPIRES: Final[int] = int(environ['JWT_REFRESH_TOKEN_EXPIRES'])

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

USER_AVATAR_MAX_CONTENT_LENGTH: Final[int] = int(environ['USER_AVATAR_MAX_CONTENT_LENGTH'])
USER_BACKGROUND_MAX_CONTENT_LENGTH: Final[int] = int(environ['USER_BACKGROUND_MAX_CONTENT_LENGTH'])
MESSAGE_FILES_MAX_CONTENT_LENGTH: Final[int] = int(environ['MESSAGE_FILES_MAX_CONTENT_LENGTH'])
