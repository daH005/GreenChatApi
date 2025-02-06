from abc import abstractmethod
from typing import Final, cast

from sqlalchemy import (
    URL,
    Engine,
    create_engine,
)
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
)

from common.singleton import AbstractSingletonMeta

__all__ = (
    'db_sync_builder',
    'db_async_builder',
)

_DEFAULT_ISOLATION_LEVEL: Final[str] = 'READ COMMITTED'


class AbstractDBBuilder(metaclass=AbstractSingletonMeta):
    _engine: Engine | AsyncEngine

    @property
    def engine(self):
        return self._engine

    @abstractmethod
    def init_session(self, url: URL | str,
                     isolation_level: str | None = _DEFAULT_ISOLATION_LEVEL,
                     ) -> None:
        raise NotImplementedError


class DBSyncBuilder(AbstractDBBuilder):

    _engine: Engine
    _session: scoped_session

    @property
    def session(self):
        return self._session

    def init_session(self, url: URL | str,
                     isolation_level: str | None = _DEFAULT_ISOLATION_LEVEL,
                     ) -> None:
        self._engine = create_engine(url=url, isolation_level=isolation_level)
        self._session = scoped_session(
            sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
            ),
        )


class DBAsyncBuilder(AbstractDBBuilder):

    _engine: AsyncEngine
    _session_maker: sessionmaker[AsyncSession]

    def init_session(self, url: URL | str,
                     isolation_level: str | None = _DEFAULT_ISOLATION_LEVEL,
                     ) -> None:
        self._engine = create_async_engine(url=url, isolation_level=isolation_level)
        self._session_maker = cast(
            sessionmaker[AsyncSession],
            sessionmaker(
                bind=cast(Engine, self._engine),
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
            ),
        )

    def new_session(self) -> AsyncSession:
        return self._session_maker()


db_sync_builder: DBSyncBuilder = DBSyncBuilder()
db_async_builder: DBAsyncBuilder = DBAsyncBuilder()
