from enum import StrEnum

from common.json_ import WebSocketMessageJSONDictMaker

__all__ = (
    'MessageType',
)


class MessageType(StrEnum):

    INTERLOCUTORS_ONLINE_STATUSES = 'interlocutorsOnlineStatuses'
    ONLINE_STATUS_TRACING_ADDING = 'onlineStatusTracingAdding'
    CHAT_MESSAGE_WAS_READ = 'chatMessageWasRead'
    NEW_UNREAD_COUNT = 'newUnreadCount'
    READ_CHAT_MESSAGES = 'readChatMessages'
    NEW_CHAT = 'newChat'
    NEW_CHAT_MESSAGE = 'newChatMessage'
    NEW_CHAT_MESSAGE_TYPING = 'newChatMessageTyping'

    def make_json_dict(self, data: dict) -> WebSocketMessageJSONDictMaker.Dict:
        return WebSocketMessageJSONDictMaker.make(
            type_=self.value,  # noqa
            data=data,
        )
