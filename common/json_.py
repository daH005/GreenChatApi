from __future__ import annotations
from enum import StrEnum
from typing import TypedDict, NotRequired
from abc import ABC, abstractmethod

from db.models import (
    User,
    ChatMessage,
    Chat,
)

__all__ = (
    'JSONKey',
    'AbstractJSONDictMaker',
    'ChatHistoryJSONDictMaker',
    'ChatMessageJSONDictMaker',
    'ChatMessageStorageIdJSONDictMaker',
    'ChatMessageFilenamesJSONDictMaker',
    'ChatMessageTypingJSONDictMaker',
    'UserChatsJSONDictMaker',
    'ChatJSONDictMaker',
    'UserJSONDictMaker',
    'AlreadyTakenFlagJSONDictMaker',
    'CodeIsValidFlagJSONDictMaker',
    'NewUnreadCountJSONDictMaker',
    'ReadChatMessagesIdsJSONDictMaker',
    'WebSocketMessageJSONDictMaker',
)


class JSONKey(StrEnum):

    ID = 'id'
    USER_ID = 'userId'
    CHAT_ID = 'chatId'
    CHAT_MESSAGE_ID = 'chatMessageId'

    FIRST_NAME = 'firstName'
    LAST_NAME = 'lastName'

    TEXT = 'text'
    CREATING_DATETIME = 'creatingDatetime'
    IS_READ = 'isRead'
    STORAGE_ID = 'storageId'

    FILENAME = 'filename'
    FILENAMES = 'filenames'

    USERNAME = 'username'
    PASSWORD = 'password'
    EMAIL = 'email'

    OFFSET_FROM_END = 'offsetFromEnd'

    CHATS = 'chats'

    MESSAGES = 'messages'

    NAME = 'name'
    IS_GROUP = 'isGroup'
    LAST_CHAT_MESSAGE = 'lastMessage'
    USERS_IDS = 'usersIds'
    UNREAD_COUNT = 'unreadCount'

    CHAT_MESSAGES_IDS = 'chatMessagesIds'

    IS_ALREADY_TAKEN = 'isAlreadyTaken'

    CODE_KEY = 'codeKey'
    CODE = 'code'
    CODE_IS_VALID = 'codeIsValid'

    TYPE = 'type'
    DATA = 'data'


class AbstractJSONDictMaker(ABC):
    Dict: TypedDict

    @staticmethod
    @abstractmethod
    def make(*args, **kwargs) -> Dict:
        raise NotImplementedError


class AlreadyTakenFlagJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        isAlreadyTaken: bool

    @staticmethod
    def make(flag: bool) -> Dict:
        return {JSONKey.IS_ALREADY_TAKEN: flag}


class CodeIsValidFlagJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        codeIsValid: bool

    @staticmethod
    def make(flag: bool) -> Dict:
        return {JSONKey.CODE_IS_VALID: flag}


class UserJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        id: int
        firstName: str
        lastName: str
        email: NotRequired[str]

    @staticmethod
    def make(user: User,
             exclude_important_info: bool = True,
             ) -> Dict:
        user_info = {
            JSONKey.ID: user.id,
            JSONKey.FIRST_NAME: user.first_name,
            JSONKey.LAST_NAME: user.last_name,
        }
        if not exclude_important_info:
            user_info[JSONKey.EMAIL] = user.email
        return user_info


class ChatHistoryJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        messages: list[ChatMessageJSONDictMaker.Dict]

    @staticmethod
    def make(chat_messages: list[ChatMessage]) -> Dict:
        return {
            JSONKey.MESSAGES: [ChatMessageJSONDictMaker.make(chat_message) for chat_message in chat_messages]
        }


class ChatMessageJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        id: int
        chatId: int
        userId: int
        text: str
        creatingDatetime: str
        isRead: bool
        storageId: int | None

    @staticmethod
    def make(chat_message: ChatMessage) -> Dict:
        return {
            JSONKey.ID: chat_message.id,
            JSONKey.CHAT_ID: chat_message.chat_id,
            JSONKey.TEXT: chat_message.text,
            JSONKey.CREATING_DATETIME: chat_message.creating_datetime.isoformat(),
            JSONKey.USER_ID: chat_message.user_id,
            JSONKey.IS_READ: chat_message.is_read,
            JSONKey.STORAGE_ID: chat_message.storage_id,
        }


class ChatMessageStorageIdJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        storageId: int

    @staticmethod
    def make(storage_id: int) -> Dict:
        return {
            JSONKey.STORAGE_ID: storage_id,
        }


class ChatMessageFilenamesJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        filenames: list[str]

    @staticmethod
    def make(filenames: list[str]) -> Dict:
        return {
            JSONKey.FILENAMES: filenames,
        }


class ChatMessageTypingJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        chatId: int
        userId: int

    @staticmethod
    def make(chat_id: int,
             user_id: int,
             ) -> Dict:
        return {
            JSONKey.CHAT_ID: chat_id,
            JSONKey.USER_ID: user_id,
        }


class UserChatsJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        chats: list[ChatJSONDictMaker.Dict]

    @staticmethod
    def make(user_chats: list[Chat],
             user_id: int,
             ) -> Dict:
        chats_for_json = []
        for chat in user_chats:
            chats_for_json.append(ChatJSONDictMaker.make(chat=chat, user_id=user_id))
        return {JSONKey.CHATS: chats_for_json}


class ChatJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        id: int
        name: str
        isGroup: bool
        lastMessage: ChatMessageJSONDictMaker.Dict | None
        usersIds: list[int]
        unreadCount: int

    @staticmethod
    def make(chat: Chat,
             user_id: int,
             ) -> Dict:
        try:
            last_message = ChatMessageJSONDictMaker.make(chat.last_message)
        except IndexError:
            last_message = None
        return {
            JSONKey.ID: chat.id,
            JSONKey.NAME: chat.name,
            JSONKey.IS_GROUP: chat.is_group,
            JSONKey.LAST_CHAT_MESSAGE: last_message,
            JSONKey.USERS_IDS: [user.id for user in chat.users()],
            JSONKey.UNREAD_COUNT: chat.unread_count_of_user(user_id=user_id).value,
        }


class NewUnreadCountJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        chatId: int
        unreadCount: int

    @staticmethod
    def make(chat_id: int,
             unread_count: int,
             ) -> Dict:
        return {
            JSONKey.CHAT_ID: chat_id,
            JSONKey.UNREAD_COUNT: unread_count,
        }


class ReadChatMessagesIdsJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        chatId: int
        chatMessagesIds: list[int]

    @staticmethod
    def make(chat_id: int,
             chat_messages_ids: list[int],
             ) -> Dict:
        return {
            JSONKey.CHAT_ID: chat_id,
            JSONKey.CHAT_MESSAGES_IDS: chat_messages_ids,
        }


class WebSocketMessageJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        type: str
        data: dict

    @staticmethod
    def make(type_: str,
             data: dict,
             ) -> Dict:
        return {
            JSONKey.TYPE: type_,
            JSONKey.DATA: data,
        }
