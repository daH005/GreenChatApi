from functools import wraps

from common.json_keys import JSONKey
from common.signals.message import SignalQueueMessage
from common.signals.queue import SignalQueue
from common.signals.signal_types import SignalType

__all__ = (
    'signal_decorator',
)

queue: SignalQueue = SignalQueue()


def signal_decorator(signal_type: SignalType):
    def decorator(func):
        @wraps(func)
        def wrapper(self, user_ids: list[int], **kwargs):
            message = SignalQueueMessage(
                user_ids=user_ids,
                message={
                    JSONKey.TYPE: signal_type,
                    JSONKey.DATA: func(self, **kwargs),
                },
            )
            queue.push(message)
        return wrapper
    return decorator
