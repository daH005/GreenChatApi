from enum import StrEnum

__all__ = (
    'EndpointName',
    'Url',
)


class EndpointName(StrEnum):
    CHAT_HISTORY = 'chat_history'
    ALL_CHATS = 'all_chats'


class Url(StrEnum):
    CHAT_HISTORY = '/chatHistory'
    ALL_CHATS = '/allChats'
