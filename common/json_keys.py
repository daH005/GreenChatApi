from enum import StrEnum


class JSONKey(StrEnum):

    ID = 'id'
    USER_ID = 'userId'
    CHAT_ID = 'chatId'
    CHAT_MESSAGE_ID = 'chatMessageId'
    CHAT_MESSAGES_IDS = 'chatMessagesIds'
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
    LAST_CHAT_MESSAGE = 'lastMessage'
    USERS_IDS = 'usersIds'
    UNREAD_COUNT = 'unreadCount'

    IS_ALREADY_TAKEN = 'isAlreadyTaken'
    CODE_IS_VALID = 'codeIsValid'

    TYPE = 'type'
    DATA = 'data'

    def __repr__(self) -> str:
        return '\'' + str(self) + '\''
