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
    CHAT_BY_INTERLOCUTOR = '/chat/byInterlocutor'
    CHAT_NEW = '/chat/new'
    CHAT_TYPING = '/chat/typing'
    CHAT_UNREAD_COUNT = '/chat/unreadCount'
    CHAT_MESSAGES = '/chat/messages'

    MESSAGE = '/message'
    MESSAGE_NEW = '/message/new'
    MESSAGE_EDIT = '/message/edit'
    MESSAGE_DELETE = '/message/delete'
    MESSAGE_READ = '/message/read'
    MESSAGE_FILES_UPDATE = '/message/files/update'
    MESSAGE_FILES_DELETE = '/message/files/delete'
    MESSAGE_FILES_NAMES = '/message/files/names'
    MESSAGE_FILES_GET = '/message/files/get'
