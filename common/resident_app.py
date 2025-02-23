from redis import Redis

from config.api import REDIS_HOST, REDIS_PORT

__all__ = (
    'resident_app',
)

resident_app: Redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)
