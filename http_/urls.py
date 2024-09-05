from enum import StrEnum

__all__ = (
    'Url',
)


class Url(StrEnum):
    EMAIL_CHECK = '/user/login/email/check'
    CODE_SEND = '/user/login/email/code/send'
    CODE_CHECK = '/user/login/email/code/check'
    LOGIN = '/user/login'
    REFRESH_ACCESS = '/user/refreshAccess'
    USER_INFO = '/user/info'
    USER_AVATAR = '/user/avatar'
    USER_BACKGROUND = '/user/background'
    USER_INFO_EDIT = '/user/info/edit'
    USER_AVATAR_EDIT = '/user/avatar/edit'
    USER_BACKGROUND_EDIT = '/user/background/edit'
    USER_CHATS = '/user/chats'
    CHAT_HISTORY = '/chat/history'
