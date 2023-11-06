from __future__ import annotations
from enum import StrEnum
from typing import TypedDict

__all__ = (
    'JSONKey',
    'AuthSocketDataJSONDict',
    'ChatMessageSocketDataJSONDict',
    'ChatJSONDict',
    'ChatMessageJSONDict',
    'UserChatsJSONDict',
    'ChatInitialDataJSONDict',
    'AuthTokenJSONDict',
    'make_chat_message_json_dict',
    'make_chat_json_dict',
    'make_user_chats_json_dict',
    'make_chat_initial_data_json_dict',
    'make_auth_token_json_dict',
)


class JSONKey(StrEnum):
    """Ключи, используемые в JSON'ах."""

    USER_ID = 'userId'
    CHAT_ID = 'chatId'
    FIRST_NAME = 'firstName'
    LAST_NAME = 'lastName'
    TEXT = 'text'
    USERNAME = 'username'
    PASSWORD = 'password'
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

    userId: int
    chatId: int
    firstName: str
    lastName: str
    text: str
    creatingDatetime: str


class UserChatsJSONDict(TypedDict):
    """Словарь со всеми чата пользователя. От каждого чата берётся только последнее сообщение."""

    chats: list[ChatInitialDataJSONDict]


class ChatInitialDataJSONDict(TypedDict):
    """Начальные данные для загрузки чата на клиенте."""

    chatId: int
    chatName: str
    lastChatMessage: str


class AuthTokenJSONDict(TypedDict):
    """Словарь с токеном авторизации."""

    authToken: str


def make_chat_json_dict(messages: list[ChatMessageJSONDict]) -> ChatJSONDict:
    """Подготавливает словарь с историей чата для отправки клиенту."""
    return {JSONKey.MESSAGES: messages}


def make_chat_message_json_dict(user_id: int,
                                chat_id: int,
                                first_name: str,
                                last_name: str,
                                text: str,
                                creating_datetime: str,  # ISO-format!
                                ) -> ChatMessageJSONDict:
    """Подготавливает словарь сообщения для отправки клиенту."""
    return {
        JSONKey.USER_ID: user_id,
        JSONKey.CHAT_ID: chat_id,
        JSONKey.FIRST_NAME: first_name,
        JSONKey.LAST_NAME: last_name,
        JSONKey.TEXT: text,
        JSONKey.CREATING_DATETIME: creating_datetime,
    }


def make_user_chats_json_dict(chats: list[ChatInitialDataJSONDict]) -> UserChatsJSONDict:
    """Подготавливает словарь для инициализации чатов на клиенте."""
    return {JSONKey.CHATS: chats}


def make_chat_initial_data_json_dict(chat_id: int,
                                     chat_name: str,
                                     last_chat_message: ChatMessageJSONDict,
                                     ) -> ChatInitialDataJSONDict:
    """Подготавливает словарь для инициализации конкретного чата на клиенте."""
    return {
        JSONKey.CHAT_ID: chat_id,
        JSONKey.CHAT_NAME: chat_name,
        JSONKey.LAST_CHAT_MESSAGE: last_chat_message,
    }


def make_auth_token_json_dict(auth_token: str) -> AuthTokenJSONDict:
    """Подготавливает словарь с токеном авторизации."""
    return {JSONKey.AUTH_TOKEN: auth_token}
