from sqlalchemy import Engine, URL, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from db.alembic_.main import make_migrations

__all__ = (
    'db_builder',
)


class DBBuilder:
    _engine: Engine
    _session: scoped_session

    def init_session(self, url: str | URL,
                     isolation_level: str | None = 'READ COMMITTED',
                     ) -> None:
        self._engine = create_engine(url=url, isolation_level=isolation_level)
        self._session = scoped_session(
            sessionmaker(autocommit=False,
                         autoflush=False,
                         expire_on_commit=False,
                         bind=self._engine,
                         )
        )

    @staticmethod
    def make_migrations() -> None:
        make_migrations()

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def session(self) -> scoped_session:
        return self._session


db_builder: DBBuilder = DBBuilder()
