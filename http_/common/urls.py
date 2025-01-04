from enum import StrEnum

__all__ = (
    'Url',
)


class Url(StrEnum):

    USER_EMAIL_CHECK = '/user/login/email/check'
    USER_CODE_SEND = '/user/login/email/code/send'
    USER_CODE_CHECK = '/user/login/email/code/check'
    USER_LOGIN = '/user/login'
    USER_LOGOUT = '/user/logout'
    USER_REFRESH_ACCESS = '/user/refreshAccess'
    USER_INFO = '/user/info'
    USER_AVATAR = '/user/avatar'
    USER_BACKGROUND = '/user/background'
    USER_INFO_EDIT = '/user/info/edit'
    USER_AVATAR_EDIT = '/user/avatar/edit'
    USER_BACKGROUND_EDIT = '/user/background/edit'
    USER_CHATS = '/user/chats'

    CHAT_HISTORY = '/chat/history'
    CHAT_MESSAGES_FILES_SAVE = '/chat/messages/files/save'
    CHAT_MESSAGES_FILES_NAMES = '/chat/messages/files/names'
    CHAT_MESSAGES_FILES_GET = '/chat/messages/files/get'
