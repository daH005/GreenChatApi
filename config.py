from os import environ
from dotenv import load_dotenv  # pip install python-dotenv
from typing import Final
from pathlib import Path
# from sqlalchemy.engine.url import URL

__all__ = (
    'HOST',
    'HTTP_PORT',
    'WEBSOCKET_PORT',
    'DB_URL',
)

load_dotenv()
BASE_DIR: Path = Path(__file__).resolve().parent

HOST: Final[str] = environ.get('HOST', 'localhost')
HTTP_PORT: Final[int] = int(environ.get('HTTP_PORT', 81))
WEBSOCKET_PORT: Final[int] = int(environ.get('WEBSOCKET_PORT', 80))
# DB_URL: URL = URL.create(
#     drivername='postgresql',
#     username='dan005',
#     password='pass',
#     host='localhost',
#     port=5432,
#     database='test_db',
# )
DB_URL: str = 'sqlite:///' + str(BASE_DIR.joinpath('db/db.db'))

if __name__ == '__main__':
    print(BASE_DIR, DB_URL)
