from typing import TypedDict
from enum import StrEnum

__all__ = (
    'JSONKey',
    'MessageJSONDict',
    'AddressedMessages',
)


class JSONKey(StrEnum):
    TYPE = 'type'
    DATA = 'data'


class MessageJSONDict(TypedDict):

    type: str
    data: dict


class AddressedMessages:

    def __init__(self) -> None:
        self._data = {}

    def add(self, user_id: int,
            message: MessageJSONDict,
            ) -> None:
        self._data.setdefault(user_id, []).append(message)

    def iter(self) -> dict[int, list[MessageJSONDict]]:
        return self._data
