from redis import Redis

from api.config import REDIS_PORT, REDIS_HOST

__all__ = (
    'app',
)

app: Redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
