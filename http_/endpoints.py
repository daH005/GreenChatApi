from enum import StrEnum

__all__ = (
    'EndpointName',
    'Url',
)


class EndpointName(StrEnum):
    CHECK_EMAIL = 'check_email'
    SEND_CODE = 'send_code'
    CHECK_CODE = 'check_code'
    LOGIN = 'login'
    REFRESH_TOKEN = 'refresh_token'
    USER_INFO = 'user_info'
    USER_AVATAR = 'user_avatar'
    USER_EDIT_INFO = 'user_edit_info'
    USER_EDIT_AVATAR = 'user_edit_avatar'
    USER_CHATS = 'user_chats'
    CHAT_HISTORY = 'chat_history'


class Url(StrEnum):
    CHECK_EMAIL = '/user/login/email/check'
    SEND_CODE = '/user/login/code/send'
    CHECK_CODE = '/user/login/code/check'
    LOGIN = '/user/login'
    REFRESH_TOKEN = '/user/refreshToken'
    USER_INFO = '/user/info'
    USER_AVATAR = '/user/avatar'
    USER_EDIT_INFO = '/user/edit/info'
    USER_EDIT_AVATAR = '/user/edit/avatar'
    USER_CHATS = '/user/chats'
    CHAT_HISTORY = '/chat/history'
