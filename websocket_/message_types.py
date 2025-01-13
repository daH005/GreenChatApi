from enum import StrEnum

from common.json_keys import JSONKey
from websocket_.base.websocket_message import WebSocketMessageJSONDict

__all__ = (
    'MessageType',
)


class MessageType(StrEnum):

    INTERLOCUTORS_ONLINE_STATUSES = 'interlocutorsOnlineStatuses'
    ONLINE_STATUS_TRACING_ADDING = 'onlineStatusTracingAdding'
    MESSAGE_WAS_READ = 'messageWasRead'
    NEW_UNREAD_COUNT = 'newUnreadCount'
    READ_MESSAGES = 'readMessages'
    NEW_CHAT = 'newChat'
    NEW_MESSAGE = 'newMessage'
    NEW_MESSAGE_TYPING = 'newMessageTyping'

    def make_json_dict(self, data: dict) -> WebSocketMessageJSONDict:
        return {
            JSONKey.TYPE: self.value,
            JSONKey.DATA: data,
        }
