from enum import StrEnum

__all__ = (
    'EndpointName',
    'Url',
)


class EndpointName(StrEnum):
    AUTH = 'auth'
    USER_INFO = 'user_info'
    USER_CHATS = 'user_chats'
    CHAT_HISTORY = 'chat_history'


class Url(StrEnum):
    AUTH = '/auth'
    USER_INFO = '/userInfo'
    USER_CHATS = '/userChats'
    CHAT_HISTORY = '/chatHistory'
