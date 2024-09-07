from enum import StrEnum
from redis import Redis

from api.config import REDIS_HOST, REDIS_PORT

__all__ = (
    'KeyPrefix',
)

_app: Redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)


class KeyPrefix(StrEnum):
    EMAIL_CODE = 'greenchat_email_code_'
    EMAIL_CODE_COUNT = 'greenchat_email_code_count_'

    def get(self, identify: str) -> str:
        return _app.get(self + identify)

    def set(self, identify: str,
            value: str | int,
            expires: float | None = None,
            ) -> None:
        _app.set(self + identify, value, ex=expires)

    def delete(self, identify: str) -> None:
        _app.delete(self + identify)

    def exists(self, identify: str) -> bool:
        return _app.exists(self + identify)
