from enum import StrEnum

__all__ = (
    'EndpointName',
    'Url',
)


class EndpointName(StrEnum):
    CHAT_HISTORY = 'chat_history'
    USER_CHATS = 'user_chats'
    AUTH = 'auth'


class Url(StrEnum):
    CHAT_HISTORY = '/chatHistory'
    USER_CHATS = '/userChats'
    AUTH = '/auth'
