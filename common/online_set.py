from typing import Final

from common.resident_app import resident_app
from common.singleton import SingletonMeta

__all__ = (
    'OnlineSet',
)


class OnlineSet(metaclass=SingletonMeta):
    _KEY: Final[str] = 'online_set'

    def add(self, user_id: int) -> None:
        resident_app.sadd(self._KEY, user_id)

    def remove(self, user_id: int) -> None:
        resident_app.srem(self._KEY, user_id)

    def exists(self, user_id: int | str) -> bool:
        return resident_app.sismember(self._KEY, str(user_id)) is 1
