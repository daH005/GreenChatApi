from __future__ import annotations

from enum import StrEnum
from typing import TypedDict

__all__ = (
    'JSONKey',
    'AuthSocketDataJSONDict',
    'ChatMessageSocketDataJSONDict',
    'ChatJSONDict',
    'ChatMessageJSONDict',
    'make_json_chat_message_dict',
    'make_json_chat_dict',
)


class JSONKey(StrEnum):
    """Ключи, используемые в JSON'ах."""

    USER_ID = 'userId'
    CHAT_ID = 'chatId'
    FIRST_NAME = 'firstName'
    LAST_NAME = 'lastName'
    TEXT = 'text'
    EMAIL = 'email'
    PASSWORD = 'password'
    CREATING_DATETIME = 'creatingDatetime'


class AuthSocketDataJSONDict(TypedDict):
    """Словарь с авторизующими данными. Поступает при первом сообщении по веб-сокету."""

    email: str
    password: str


class ChatMessageSocketDataJSONDict(TypedDict):
    """Рядовое сообщение в заданный чат, поступающее на сервер веб-сокета.
    Предполагается, что на данном этапе пользователь уже авторизован.
    """

    chat_id: int
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


def make_json_chat_dict(messages: list[ChatMessageJSONDict]) -> ChatJSONDict:
    """Подготавливает словарь с историей чата к отправке клиенту."""
    return dict(messages=messages)


def make_json_chat_message_dict(user_id: int,
                                chat_id: int,
                                first_name: str,
                                last_name: str,
                                text: str,
                                creating_datetime: str,  # ISO-format!
                                ) -> ChatMessageJSONDict:
    """Подготавливает словарь сообщения к отправке клиенту."""
    return {
        JSONKey.USER_ID: user_id,
        JSONKey.CHAT_ID: chat_id,
        JSONKey.FIRST_NAME: first_name,
        JSONKey.LAST_NAME: last_name,
        JSONKey.TEXT: text,
        JSONKey.CREATING_DATETIME: creating_datetime,
    }
