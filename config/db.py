from os import environ
from typing import Final

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()

__all__ = (
    'DB_URL',
    'DB_TEST_URL',
    'DEFAULT_TRANSACTION_RETRY_MAX_ATTEMPTS'
)

DB_URL: URL = URL.create(
    drivername=environ['DB_DRIVERNAME'],
    username=environ['DB_USERNAME'],
    password=environ['DB_PASSWORD'],
    host=environ['DB_HOST'],
    port=int(environ['DB_PORT']),
    database=environ['DB_NAME'],
)
DB_TEST_URL: URL = DB_URL.set(
    username=environ['DB_TEST_USERNAME'],
    password=environ['DB_TEST_PASSWORD'],
    host=environ['DB_TEST_HOST'],
    port=int(environ['DB_TEST_PORT']),
    database=environ['DB_TEST_NAME'],
)

DEFAULT_TRANSACTION_RETRY_MAX_ATTEMPTS: Final[int] = int(environ['DEFAULT_TRANSACTION_RETRY_MAX_ATTEMPTS'])
