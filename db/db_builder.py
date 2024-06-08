from __future__ import annotations

from sqlalchemy import Engine, URL, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from api.db.alembic_.init import make_migrations

__all__ = (
    'DBBuilder',
)


class DBBuilder:
    engine: Engine
    session: scoped_session

    @classmethod
    def init_session(cls, url: str | URL) -> None:
        cls.engine = create_engine(url=url)
        cls.session = scoped_session(
            sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=cls.engine,
                         )
        )

    @classmethod
    def make_migrations(cls) -> None:
        make_migrations()
