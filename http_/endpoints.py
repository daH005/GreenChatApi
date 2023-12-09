from enum import StrEnum

__all__ = (
    'EndpointName',
    'Url',
)


class EndpointName(StrEnum):
    REG = 'reg'
    AUTH = 'auth'
    REFRESH_TOKEN = 'refresh_token'
    USER_INFO = 'user_info'
    USER_CHATS = 'user_chats'
    CHAT_HISTORY = 'chat_history'


class Url(StrEnum):
    REG = '/user/new'
    AUTH = '/user/auth'
    REFRESH_TOKEN = '/user/refreshToken'
    USER_INFO = '/user/info'
    USER_CHATS = '/user/chats'
    CHAT_HISTORY = '/chats/<int:chat_id>/history'
