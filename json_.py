from __future__ import annotations
from enum import StrEnum
from typing import TypedDict, NotRequired
from abc import ABC, abstractmethod

from api.db.models import (
    User,
    ChatMessage,
    Chat,
)

__all__ = (
    'JSONKey',
    'AbstractJSONDictMaker',
    'ChatHistoryJSONDictMaker',
    'ChatMessageJSONDictMaker',
    'ChatMessageTypingJSONDictMaker',
    'UserChatsJSONDictMaker',
    'ChatInfoJSONDictMaker',
    'JWTTokenJSONDictMaker',
    'UserInfoJSONDictMaker',
    'AlreadyTakenFlagJSONDictMaker',
    'CodeIsValidFlagJSONDictMaker',
)


class JSONKey(StrEnum):
    """Набор унифицированных имён, используемых в структурах данных,
    передаваемых по сети (http, сокет).
    """

    ID = 'id'
    USER_ID = 'userId'
    CHAT_ID = 'chatId'

    FIRST_NAME = 'firstName'
    LAST_NAME = 'lastName'

    TEXT = 'text'
    CREATING_DATETIME = 'creatingDatetime'

    USERNAME = 'username'
    PASSWORD = 'password'
    EMAIL = 'email'

    JWT_TOKEN = 'JWTToken'

    OFFSET_FROM_END = 'offsetFromEnd'

    CHATS = 'chats'

    MESSAGES = 'messages'

    NAME = 'name'
    IS_GROUP = 'isGroup'
    LAST_CHAT_MESSAGE = 'lastMessage'
    USERS_IDS = 'usersIds'

    IS_ALREADY_TAKEN = 'isAlreadyTaken'
    CODE = 'code'
    CODE_IS_VALID = 'codeIsValid'


class AbstractJSONDictMaker(ABC):
    """Интерфейс класса для формирования JSON-словарей.
    P.S. `TypedDict` не позволяет определять в нём методы. Если бы это было возможно,
    то решение оказалось бы проще - метод `make` был бы помещен прямо в `TypedDict`.
    """

    Dict: TypedDict

    @staticmethod
    @abstractmethod
    def make(*args, **kwargs) -> Dict:
        raise NotImplementedError


class JWTTokenJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):
        JWTToken: str

    @staticmethod
    def make(jwt_token: str) -> Dict:
        return {JSONKey.JWT_TOKEN: jwt_token}


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


class UserInfoJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):

        id: int
        firstName: str
        lastName: str
        username: NotRequired[str]
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
            user_info[JSONKey.USERNAME] = user.username
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
        text: str
        creatingDatetime: str
        userId: int

    @staticmethod
    def make(chat_message: ChatMessage) -> Dict:
        return {
            JSONKey.ID: chat_message.id,
            JSONKey.CHAT_ID: chat_message.chat_id,
            JSONKey.TEXT: chat_message.text,
            JSONKey.CREATING_DATETIME: chat_message.creating_datetime.isoformat(),
            JSONKey.USER_ID: chat_message.user_id,
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
        chats: list[ChatInfoJSONDictMaker.Dict]

    @staticmethod
    def make(user_chats: list[Chat]) -> Dict:
        chats_for_json = []
        for chat in user_chats:
            chats_for_json.append(ChatInfoJSONDictMaker.make(chat))
        return {JSONKey.CHATS: chats_for_json}


class ChatInfoJSONDictMaker(AbstractJSONDictMaker):

    class Dict(TypedDict):

        id: int
        name: str
        isGroup: bool
        lastMessage: ChatMessageJSONDictMaker.Dict | None
        usersIds: list[int]

    @staticmethod
    def make(chat: Chat) -> Dict:
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
        }
