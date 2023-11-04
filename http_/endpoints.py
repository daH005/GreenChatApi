from enum import StrEnum

__all__ = (
    'EndpointName',
    'Url',
)


class EndpointName(StrEnum):
    CHAT_HISTORY = 'chat_history'
    ALL_LAST_CHATS_MESSAGES = 'all_last_chats_messages'


class Url(StrEnum):
    CHAT_HISTORY = '/chatHistory'
    ALL_LAST_CHATS_MESSAGES = '/allLastChatsMessages'
