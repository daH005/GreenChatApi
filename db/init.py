from config import DB_URL
from db.builder import db_builder

__all__ = (
    'init_db',
)


def init_db() -> None:
    db_builder.init_session(DB_URL)


if __name__ == '__main__':
    init_db()
    db_builder.make_migrations()
