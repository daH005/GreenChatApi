from celery import Celery

from api.config import REDIS_URL

__all__ = (
    'app',
)

app: Celery = Celery(broker=REDIS_URL)
