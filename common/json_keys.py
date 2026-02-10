from enum import StrEnum

__all__ = (
    'JSONKey',
)


class JSONKey(StrEnum):

    ID = 'id'
    USER_ID = 'userId'
    CHAT_ID = 'chatId'
    MESSAGE_ID = 'messageId'
    REPLIED_MESSAGE_ID = 'repliedMessageId'
    MESSAGE_IDS = 'messageIds'
    INTERLOCUTOR_ID = 'interlocutorId'

    EMAIL = 'email'
    FIRST_NAME = 'firstName'
    LAST_NAME = 'lastName'
    IS_ONLINE = 'isOnline'

    TEXT = 'text'
    CREATING_DATETIME = 'creatingDatetime'
    IS_READ = 'isRead'
    HAS_FILES = 'hasFiles'
    REPLIED_MESSAGE = 'repliedMessage'

    FILENAMES = 'filenames'
    FILENAME = 'filename'

    OFFSET = 'offset'
    SIZE = 'size'

    NAME = 'name'
    IS_GROUP = 'isGroup'
    USER_IDS = 'userIds'
    UNREAD_COUNT = 'unreadCount'

    IS_THAT = 'isThat'

    TYPE = 'type'
    DATA = 'data'

    def __repr__(self) -> str:
        return '\'' + str(self) + '\''
