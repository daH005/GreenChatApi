from enum import StrEnum

__all__ = (
    'Url',
)


class Url(StrEnum):

    USER_CODE_SEND = '/user/login/email/code/send'
    USER_CODE_CHECK = '/user/login/email/code/check'
    USER_LOGIN = '/user/login'
    USER_LOGOUT = '/user/logout'
    USER_REFRESH_ACCESS = '/user/refreshAccess'
    USER = '/user'
    USER_EDIT = '/user/edit'
    USER_AVATAR = '/user/avatar'
    USER_AVATAR_EDIT = '/user/avatar/edit'
    USER_BACKGROUND = '/user/background'
    USER_BACKGROUND_EDIT = '/user/background/edit'
    USER_CHATS = '/user/chats'

    CHAT = '/chat'
    CHAT_NEW = '/chat/new'
    CHAT_TYPING = '/chat/typing'
    CHAT_UNREAD_COUNT = '/chat/unreadCount'
    CHAT_MESSAGE = '/chat/message'
    CHAT_MESSAGE_NEW = '/chat/message/new'
    CHAT_MESSAGE_READ = '/chat/message/read'
    CHAT_MESSAGES = '/chat/messages'
    CHAT_MESSAGE_FILES_SAVE = '/chat/message/files/save'
    CHAT_MESSAGE_FILES_NAMES = '/chat/message/files/names'
    CHAT_MESSAGE_FILES_GET = '/chat/message/files/get'
