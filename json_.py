from __future__ import annotations
from enum import StrEnum
from typing import TypedDict

from api.db.models import (
    User,
    ChatMessage,
    Chat,
    UserChatMatch,
)

__all__ = (
    'JSONKey',
    'AuthSocketDataJSONDict',
    'ChatMessageSocketDataJSONDict',
    'ChatJSONDict',
    'ChatMessageJSONDict',
    'UserChatsJSONDict',
    'ChatInitialDataJSONDict',
    'AuthTokenJSONDict',
    'JSONDictPreparer',
)


class JSONKey(StrEnum):
    """Ключи, используемые в JSON'ах."""

    ID = 'id'
    USER_ID = 'userId'
    CHAT_ID = 'chatId'
    FIRST_NAME = 'firstName'
    LAST_NAME = 'lastName'
    TEXT = 'text'
    USERNAME = 'username'
    PASSWORD = 'password'
    EMAIL = 'email'
    CREATING_DATETIME = 'creatingDatetime'
    AUTH_TOKEN = 'authToken'
    SKIP_FROM_END_COUNT = 'skipFromEndCount'
    CHAT_NAME = 'chatName'
    MESSAGES = 'messages'
    CHATS = 'chats'
    LAST_CHAT_MESSAGE = 'lastChatMessage'


class AuthSocketDataJSONDict(TypedDict):
    """Словарь с авторизующими данными. Поступает при первом сообщении по веб-сокету."""

    authToken: str


class ChatMessageSocketDataJSONDict(TypedDict):
    """Рядовое сообщение в заданный чат, поступающее на сервер веб-сокета.
    Предполагается, что на данном этапе пользователь уже авторизован.
    """

    chatId: int
    text: str


class ChatJSONDict(TypedDict):
    """Словарь с историей чата. Высылается в качестве ответа на HTTP-запрос."""

    messages: list[ChatMessageJSONDict]


class ChatMessageJSONDict(TypedDict):
    """Рядовое сообщение, отправляемое клиенту по HTTP / Websocket."""

    id: int
    userId: int
    chatId: int
    # FixMe: По хорошему тону лучше бы сделать ключ 'user' с этими данными.
    firstName: str
    lastName: str
    text: str
    creatingDatetime: str


class UserChatsJSONDict(TypedDict):
    """Словарь со всеми чата пользователя. От каждого чата берётся только последнее сообщение."""

    chats: list[ChatInitialDataJSONDict]


class ChatInitialDataJSONDict(TypedDict):
    """Начальные данные для загрузки чата на клиенте."""

    id: int
    chatName: str
    lastChatMessage: ChatMessageJSONDict


class AuthTokenJSONDict(TypedDict):
    """Словарь с токеном авторизации."""

    authToken: str


class UserInfoJSONDict(TypedDict):
    """Вся информация о пользователе."""

    id: int
    username: str
    firstName: str
    lastName: str
    email: str


class JSONDictPreparer:

    @classmethod
    def chat_history(cls, chat: Chat,
                     skip_from_end_count: int | None,
                     ) -> ChatJSONDict:
        if skip_from_end_count is not None:
            if skip_from_end_count > 0:
                skip_from_end_count = -skip_from_end_count
        return {
            JSONKey.MESSAGES: [cls.chat_message(chat_message) for chat_message in chat.messages[:skip_from_end_count]]
        }

    @classmethod
    def chat_message(cls, chat_message: ChatMessage) -> ChatMessageJSONDict:
        return {
            JSONKey.ID: chat_message.id,
            JSONKey.USER_ID: chat_message.user_id,
            JSONKey.CHAT_ID: chat_message.chat_id,
            JSONKey.FIRST_NAME: chat_message.first_name,
            JSONKey.LAST_NAME: chat_message.last_name,
            JSONKey.TEXT: chat_message.text,
            JSONKey.CREATING_DATETIME: chat_message.creating_datetime,
        }

    @classmethod
    def user_chats(cls, user_chats: list[Chat],
                   user: User,
                   ) -> UserChatsJSONDict:
        result_chats = []
        for chat in user_chats:
            result_chats.append({
                JSONKey.ID: chat.id,
                JSONKey.CHAT_NAME: UserChatMatch.chat_name(user_id=user.id, chat_id=chat.id),
                JSONKey.LAST_CHAT_MESSAGE: cls.chat_message(chat.last_message),
            })
        return {JSONKey.CHATS: result_chats}

    @classmethod
    def auth_token(cls, user: User) -> AuthTokenJSONDict:
        return {JSONKey.AUTH_TOKEN: user.auth_token}

    @classmethod
    def user_info(cls, user: User) -> UserInfoJSONDict:
        return {
            JSONKey.ID: user.id,
            JSONKey.USERNAME: user.username,
            JSONKey.FIRST_NAME: user.first_name,
            JSONKey.LAST_NAME: user.last_name,
            JSONKey.EMAIL: user.email,
        }
