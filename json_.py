from __future__ import annotations
from enum import StrEnum
from typing import TypedDict, NotRequired

from api.db.models import (
    User,
    ChatMessage,
    Chat,
)

__all__ = (
    'JSONKey',
    'ChatHistoryJSONDict',
    'ChatMessageJSONDict',
    'UserChatsJSONDict',
    'ChatInfoJSONDict',
    'JWTTokenJSONDict',
    'UserInfoJSONDict',
    'AlreadyTakenFlagJSONDict',
    'CodeIsValidFlagJSONDict',
    'JSONDictPreparer',
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
    USER = 'user'

    USERNAME = 'username'
    PASSWORD = 'password'
    EMAIL = 'email'

    JWT_TOKEN = 'JWTToken'

    OFFSET_FROM_END = 'offsetFromEnd'

    CHATS = 'chats'

    MESSAGES = 'messages'

    NAME = 'name'
    USERS = 'users'
    IS_GROUP = 'isGroup'
    LAST_CHAT_MESSAGE = 'lastMessage'
    USERS_IDS = 'usersIds'

    IS_ALREADY_TAKEN = 'isAlreadyTaken'
    CODE = 'code'
    CODE_IS_VALID = 'codeIsValid'


class JWTTokenJSONDict(TypedDict):
    JWTToken: str


class AlreadyTakenFlagJSONDict(TypedDict):
    isAlreadyTaken: bool


class CodeIsValidFlagJSONDict(TypedDict):
    codeIsValid: bool


class UserInfoJSONDict(TypedDict):

    id: int
    firstName: str
    lastName: str
    username: NotRequired[str]
    email: NotRequired[str]


class ChatHistoryJSONDict(TypedDict):
    messages: list[ChatMessageJSONDict]


class ChatMessageJSONDict(TypedDict):

    id: int
    chatId: int
    text: str
    creatingDatetime: str
    user: UserInfoJSONDict


class UserChatsJSONDict(TypedDict):
    chats: list[ChatInfoJSONDict]


class ChatInfoJSONDict(TypedDict):

    id: int
    name: str
    isGroup: bool
    lastMessage: ChatMessageJSONDict | None
    users: list[UserInfoJSONDict]


class JSONDictPreparer:

    @classmethod
    def prepare_jwt_token(cls, jwt_token: str) -> JWTTokenJSONDict:
        return {JSONKey.JWT_TOKEN: jwt_token}

    @classmethod
    def prepare_already_taken(cls, flag: bool) -> AlreadyTakenFlagJSONDict:
        return {JSONKey.IS_ALREADY_TAKEN: flag}

    @classmethod
    def prepare_code_is_valid(cls, flag: bool) -> CodeIsValidFlagJSONDict:
        return {JSONKey.CODE_IS_VALID: flag}

    @classmethod
    def prepare_user_chats(cls, user_chats: list[Chat]) -> UserChatsJSONDict:
        chats_for_json = []
        for chat in user_chats:
            chats_for_json.append(cls.prepare_chat_info(chat))
        return {JSONKey.CHATS: chats_for_json}

    @classmethod
    def prepare_chat_info(cls, chat: Chat) -> ChatInfoJSONDict:
        try:
            last_message = cls.prepare_chat_message(chat.last_message)
        except IndexError:
            last_message = None
        return {
            JSONKey.ID: chat.id,
            JSONKey.NAME: chat.name,
            JSONKey.IS_GROUP: chat.is_group,
            JSONKey.LAST_CHAT_MESSAGE: last_message,
            JSONKey.USERS: [cls.prepare_user_info(user) for user in chat.users()],
        }

    @classmethod
    def prepare_user_info(cls, user: User,
                          exclude_important_info: bool = True,
                          ) -> UserInfoJSONDict:
        user_info = {
            JSONKey.ID: user.id,
            JSONKey.FIRST_NAME: user.first_name,
            JSONKey.LAST_NAME: user.last_name,
        }
        if not exclude_important_info:
            user_info[JSONKey.EMAIL] = user.email
            user_info[JSONKey.USERNAME] = user.username
        return user_info

    @classmethod
    def prepare_chat_history(cls, chat_messages: list[ChatMessage]) -> ChatHistoryJSONDict:
        return {
            JSONKey.MESSAGES: [cls.prepare_chat_message(chat_message) for chat_message in chat_messages]
        }

    @classmethod
    def prepare_chat_message(cls, chat_message: ChatMessage) -> ChatMessageJSONDict:
        return {
            JSONKey.ID: chat_message.id,
            JSONKey.CHAT_ID: chat_message.chat_id,
            JSONKey.TEXT: chat_message.text,
            JSONKey.CREATING_DATETIME: chat_message.creating_datetime.isoformat(),
            JSONKey.USER: cls.prepare_user_info(chat_message.user),
        }
