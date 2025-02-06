from config import DB_URL
from db.builders import db_sync_builder

__all__ = (
    'init_db',
)


def init_db() -> None:
    db_sync_builder.init_session(DB_URL)
