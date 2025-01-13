from enum import StrEnum

__all__ = (
    'JSONKey',
)


class JSONKey(StrEnum):

    ID = 'id'
    USER_ID = 'userId'
    CHAT_ID = 'chatId'
    MESSAGE_ID = 'messageId'
    MESSAGE_IDS = 'messageIds'
    STORAGE_ID = 'storageId'
    INTERLOCUTOR_ID = 'interlocutorId'

    EMAIL = 'email'
    FIRST_NAME = 'firstName'
    LAST_NAME = 'lastName'
    IS_ONLINE = 'isOnline'

    TEXT = 'text'
    CREATING_DATETIME = 'creatingDatetime'
    IS_READ = 'isRead'

    FILENAME = 'filename'
    FILENAMES = 'filenames'

    MESSAGES = 'messages'
    OFFSET = 'offset'

    CHATS = 'chats'

    NAME = 'name'
    IS_GROUP = 'isGroup'
    LAST_MESSAGE = 'lastMessage'
    USER_IDS = 'userIds'
    UNREAD_COUNT = 'unreadCount'

    CODE_IS_VALID = 'codeIsValid'

    TYPE = 'type'
    DATA = 'data'

    def __repr__(self) -> str:
        return '\'' + str(self) + '\''
