from db.init import init_db
from http_.app import app

__all__ = (
    'app',
)

init_db()
