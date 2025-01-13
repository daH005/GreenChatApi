from enum import StrEnum


class JSONKey(StrEnum):

    ID = 'id'
    USER_ID = 'userId'
    CHAT_ID = 'chatId'
    MESSAGE_ID = 'messageId'
    MESSAGE_IDS = 'messageIds'
    STORAGE_ID = 'storageId'

    EMAIL = 'email'
    FIRST_NAME = 'firstName'
    LAST_NAME = 'lastName'

    TEXT = 'text'
    CREATING_DATETIME = 'creatingDatetime'
    IS_READ = 'isRead'

    FILENAME = 'filename'
    FILENAMES = 'filenames'

    MESSAGES = 'messages'
    OFFSET_FROM_END = 'offsetFromEnd'

    CHATS = 'chats'

    NAME = 'name'
    IS_GROUP = 'isGroup'
    LAST_MESSAGE = 'lastMessage'
    USER_IDS = 'userIds'
    UNREAD_COUNT = 'unreadCount'

    IS_ALREADY_TAKEN = 'isAlreadyTaken'
    CODE_IS_VALID = 'codeIsValid'

    TYPE = 'type'
    DATA = 'data'

    def __repr__(self) -> str:
        return '\'' + str(self) + '\''
