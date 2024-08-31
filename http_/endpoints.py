from enum import StrEnum

__all__ = (
    'Url',
)


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
