from __future__ import annotations
from typing import TypedDict
from enum import StrEnum

from api.json_ import AbstractJSONDictMaker

__all__ = (
    'MessageType',
    'JSONKey',
    'MessageJSONDictMaker',
    'AddressedMessages',
)


class JSONKey(StrEnum):
    TYPE = 'type'
    DATA = 'data'


class MessageJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):

        type: str
        data: dict

    @staticmethod
    def make(type_: str,
             data: dict,
             ) -> Dict:
        return {
            JSONKey.TYPE: type_,
            JSONKey.DATA: data,
        }


class MessageType(StrEnum):

    INTERLOCUTORS_ONLINE_INFO = 'interlocutorsOnlineInfo'
    NEW_INTERLOCUTOR_ONLINE_STATUS_ADDING = 'newInterlocutorOnlineStatusAdding'
    NEW_CHAT = 'newChat'
    NEW_CHAT_MESSAGE = 'newChatMessage'
    NEW_CHAT_MESSAGE_TYPING = 'newChatMessageTyping'

    def make_json_dict(self, data: dict) -> MessageJSONDictMaker.Dict:
        return MessageJSONDictMaker.make(
            type_=self.value(),
            data=data,
        )


class AddressedMessages:

    def __init__(self) -> None:
        self._data = {}

    def add(self, user_id: int,
            message: MessageJSONDictMaker.Dict,
            ) -> None:
        self._data.setdefault(user_id, []).append(message)

    def iter(self) -> dict[int, list[MessageJSONDictMaker.Dict]]:
        return self._data
