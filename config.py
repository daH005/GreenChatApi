from os import environ
from dotenv import load_dotenv  # pip install python-dotenv
from typing import Final
from pathlib import Path
from sqlalchemy.engine.url import URL

__all__ = (
    'HOST',
    'HTTP_PORT',
    'WEBSOCKET_PORT',
    'DB_URL',
)

load_dotenv()
# Абсолютный путь к папке проекта `api`.
BASE_DIR: Path = Path(__file__).resolve().parent
# Хост общий для HTTP и WebSocket.
HOST: Final[str] = environ.get('HOST', 'localhost')
HTTP_PORT: Final[int] = int(environ.get('HTTP_PORT', 81))
WEBSOCKET_PORT: Final[int] = int(environ.get('WEBSOCKET_PORT', 80))
DB_URL: URL = URL.create(
    drivername=environ['DB_DRIVERNAME'],
    username=environ['DB_USERNAME'],
    password=environ['DB_PASSWORD'],
    host=environ['DB_HOST'],
    port=int(environ['DB_PORT']),
    database=environ['DB_NAME'],
)

if __name__ == '__main__':
    print(BASE_DIR, DB_URL)
