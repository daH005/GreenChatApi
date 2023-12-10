from enum import StrEnum

__all__ = (
    'EndpointName',
    'Url',
)


class EndpointName(StrEnum):
    REG = 'reg'
    CHECK_USERNAME = 'check_username'
    CHECK_EMAIL = 'check_email'
    AUTH = 'auth'
    REFRESH_TOKEN = 'refresh_token'
    USER_INFO = 'user_info'
    USER_CHATS = 'user_chats'
    CHAT_HISTORY = 'chat_history'


class Url(StrEnum):
    REG = '/user/new'
    CHECK_USERNAME = '/user/new/check/username'
    CHECK_EMAIL = '/user/new/check/email'
    AUTH = '/user/auth'
    REFRESH_TOKEN = '/user/refreshToken'
    USER_INFO = '/user/info'
    USER_CHATS = '/user/chats'
    CHAT_HISTORY = '/chats/<int:chat_id>/history'
