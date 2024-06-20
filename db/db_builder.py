from sqlalchemy import Engine, URL, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from api.db.alembic_.init import make_migrations

__all__ = (
    'DBBuilder',
)


class DBBuilder:
    _engine: Engine
    _session: scoped_session

    @classmethod
    def init_session(cls, url: str | URL) -> None:
        cls._engine = create_engine(url=url)
        cls._session = scoped_session(
            sessionmaker(autocommit=False,
                         autoflush=False,
                         expire_on_commit=False,
                         bind=cls._engine,
                         )
        )

    @classmethod
    def make_migrations(cls) -> None:
        make_migrations()

    @classmethod
    @property
    def engine(cls) -> Engine:
        return cls._engine

    @classmethod
    @property
    def session(cls) -> scoped_session:
        return cls._session
