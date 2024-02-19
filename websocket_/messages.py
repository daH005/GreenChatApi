from typing import TypedDict
from enum import StrEnum

__all__ = (
    'MessageTypes',
    'JSONKey',
    'MessageJSONDict',
    'AddressedMessages',
)


class MessageTypes:

    INTERLOCUTORS_ONLINE_INFO = 'interlocutorsOnlineInfo'
    NEW_INTERLOCUTOR_ONLINE_STATUS_ADDING = 'newInterlocutorOnlineStatusAdding'
    NEW_CHAT = 'newChat'
    NEW_CHAT_MESSAGE = 'newChatMessage'
    NEW_CHAT_MESSAGE_TYPING = 'newChatMessageTyping'


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
