import json
from typing import Final

from common.hinting import raises
from common.resident_app import resident_app
from common.singleton import SingletonMeta
from common.signals.exceptions import SignalQueueIsEmptyException
from common.signals.message import SignalQueueMessage

__all__ = (
    'SignalQueue',
)


class SignalQueue(metaclass=SingletonMeta):
    _KEY: Final[str] = 'signals'

    def push(self, message: SignalQueueMessage) -> None:
        resident_app.rpush(self._KEY, self._dump(message))

    @staticmethod
    def _dump(message: SignalQueueMessage) -> str:
        return json.dumps(message._asdict())

    @raises(SignalQueueIsEmptyException)
    def pop(self) -> SignalQueueMessage:
        dumped_message: str | None = resident_app.lpop(self._KEY)
        if not dumped_message:
            raise SignalQueueIsEmptyException
        return self._load(dumped_message)

    @staticmethod
    def _load(dumped_message: str) -> SignalQueueMessage:
        kwargs = json.loads(dumped_message)
        return SignalQueueMessage(**kwargs)
