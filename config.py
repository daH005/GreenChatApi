from os import environ
from dotenv import load_dotenv  # pip install python-dotenv
from typing import Final
from pathlib import Path
from sqlalchemy.engine.url import URL

__all__ = (
    'BASE_DIR',
    'HOST',
    'HTTP_PORT',
    'WEBSOCKET_PORT',
    'CORS_ORIGINS',
    'JWT_SECRET_KEY',
    'JWT_ALGORITHM',
    'JWT_ACCESS_TOKEN_EXPIRES',
    'DB_URL',
)

load_dotenv()
# Абсолютный путь к папке проекта `api`.
BASE_DIR: Path = Path(__file__).resolve().parent
# Хост общий для HTTP и WebSocket.
HOST: Final[str] = environ['HOST']
# Порт для REST api.
HTTP_PORT: Final[int] = int(environ['HTTP_PORT'])
# Порт для веб-сокета.
WEBSOCKET_PORT: Final[int] = int(environ['WEBSOCKET_PORT'])
# Домены для CORS, с которых мы принимаем запросы.
CORS_ORIGINS: Final[list[str]] = environ['CORS_ORIGINS'].split(',')
# JWT-токен для REST api.
JWT_SECRET_KEY: Final[str] = environ['JWT_SECRET_KEY']
# JWT-алгоритм для шифрования и дешифрования.
JWT_ALGORITHM: Final[str] = environ['JWT_ALGORITHM']
# Срок жизни каждого JWT-токена (в секундах).
JWT_ACCESS_TOKEN_EXPIRES: Final[int] = int(environ['JWT_ACCESS_TOKEN_EXPIRES'])
# URL для подключения к БД.
DB_URL: URL = URL.create(
    drivername=environ['DB_DRIVERNAME'],
    username=environ['DB_USERNAME'],
    password=environ['DB_PASSWORD'],
    host=environ['DB_HOST'],
    port=int(environ['DB_PORT']),
    database=environ['DB_NAME'],
)

if __name__ == '__main__':
    print(BASE_DIR)
    print(DB_URL)
    print(CORS_ORIGINS)
    print(JWT_SECRET_KEY)
