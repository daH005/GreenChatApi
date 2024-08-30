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
    USER_BACKGROUND = 'user_background'
    USER_EDIT_INFO = 'user_edit_info'
    USER_EDIT_AVATAR = 'user_edit_avatar'
    USER_EDIT_BACKGROUND = 'user_edit_background'
    USER_CHATS = 'user_chats'
    CHAT_HISTORY = 'chat_history'


class Url(StrEnum):
    CHECK_EMAIL = '/user/login/email/check'
    SEND_CODE = '/user/login/email/code/send'
    CHECK_CODE = '/user/login/email/code/check'
    LOGIN = '/user/login'
    REFRESH_TOKEN = '/user/refreshToken'
    USER_INFO = '/user/info'
    USER_AVATAR = '/user/avatar'
    USER_BACKGROUND = '/user/background'
    USER_EDIT_INFO = '/user/info/edit'
    USER_EDIT_AVATAR = '/user/avatar/edit'
    USER_EDIT_BACKGROUND = '/user/background/edit'
    USER_CHATS = '/user/chats'
    CHAT_HISTORY = '/chat/history'
