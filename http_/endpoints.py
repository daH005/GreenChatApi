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
    AUTH = '/user/auth'
    USER_INFO = '/user/info'
    USER_CHATS = '/user/chats'
    CHAT_HISTORY = '/chats/<int:chat_id>/history'
