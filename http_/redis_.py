from redis import Redis  # pip install redis

from api.config import REDIS_HOST, REDIS_PORT

__all__ = (
    'app',
)

app: Redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
