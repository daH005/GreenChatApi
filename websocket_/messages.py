from __future__ import annotations
from typing import TypedDict
from enum import StrEnum

from api.common.json_ import AbstractJSONDictMaker

__all__ = (
    'MessageType',
    'JSONKey',
    'MessageJSONDictMaker',
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

    INTERLOCUTORS_ONLINE_STATUSES = 'interlocutorsOnlineStatuses'
    ONLINE_STATUS_TRACING_ADDING = 'onlineStatusTracingAdding'
    CHAT_MESSAGE_WAS_READ = 'chatMessageWasRead'
    NEW_UNREAD_COUNT = 'newUnreadCount'
    READ_CHAT_MESSAGES = 'readChatMessages'
    NEW_CHAT = 'newChat'
    NEW_CHAT_MESSAGE = 'newChatMessage'
    NEW_CHAT_MESSAGE_TYPING = 'newChatMessageTyping'

    def make_json_dict(self, data: dict) -> MessageJSONDictMaker.Dict:
        return MessageJSONDictMaker.make(
            type_=self.value,  # noqa
            data=data,
        )
