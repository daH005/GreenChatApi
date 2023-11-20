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
    'AuthWebSocketDataJSONDict',
    'ChatMessageWebSocketDataJSONDict',
    'ChatHistoryJSONDict',
    'ChatMessageJSONDict',
    'UserChatsJSONDict',
    'ChatInitialDataJSONDict',
    'AuthTokenJSONDict',
    'UserInfoJSONDict',
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
    OFFSET_FROM_END = 'offsetFromEnd'
    NAME = 'name'
    MESSAGES = 'messages'
    CHATS = 'chats'
    LAST_CHAT_MESSAGE = 'lastMessage'
    USER = 'user'


class AuthWebSocketDataJSONDict(TypedDict):
    """Словарь с авторизующими данными. Поступает при первом сообщении по веб-сокету."""

    authToken: str


class ChatMessageWebSocketDataJSONDict(TypedDict):
    """Рядовое сообщение в заданный чат, поступающее на сервер веб-сокета.
    Предполагается, что на данном этапе пользователь уже авторизован.
    """

    chatId: int
    text: str


class AuthTokenJSONDict(TypedDict):
    """Словарь с токеном авторизации."""

    authToken: str


class UserInfoJSONDict(TypedDict):
    """Вся информация о пользователе."""

    id: int
    username: str
    firstName: str
    lastName: str
    email: NotRequired[str]


class ChatHistoryJSONDict(TypedDict):
    """Словарь с историей чата. Высылается в качестве ответа на HTTP-запрос."""

    messages: list[ChatMessageJSONDict]


class ChatMessageJSONDict(TypedDict):
    """Рядовое сообщение, отправляемое клиенту по HTTP / Websocket."""

    id: int
    chatId: int
    user: UserInfoJSONDict
    text: str
    creatingDatetime: str


class UserChatsJSONDict(TypedDict):
    """Словарь со всеми чата пользователя. От каждого чата берётся только последнее сообщение."""

    chats: list[ChatInitialDataJSONDict]


class ChatInitialDataJSONDict(TypedDict):
    """Начальные данные для загрузки чата на клиенте."""

    id: int
    name: str
    lastChatMessage: ChatMessageJSONDict


class JSONDictPreparer:
    """Подготовитель словарей данных с ключами в стиле lowerCamelCase
    для их дальнейшей отправки в сеть по HTTP / WebSocket.
    """

    @classmethod
    def prepare_auth_token(cls, auth_token: str) -> AuthTokenJSONDict:
        return {JSONKey.AUTH_TOKEN: auth_token}

    @classmethod
    def prepare_user_info(cls, user: User,
                          exclude_important_info: bool = True,
                          ) -> UserInfoJSONDict:
        user_info = {
            JSONKey.ID: user.id,
            JSONKey.USERNAME: user.username,
            JSONKey.FIRST_NAME: user.first_name,
            JSONKey.LAST_NAME: user.last_name,
        }
        if not exclude_important_info:
            user_info[JSONKey.EMAIL] = user.email
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
            JSONKey.USER: cls.prepare_user_info(chat_message.user),
            JSONKey.TEXT: chat_message.text,
            JSONKey.CREATING_DATETIME: chat_message.creating_datetime.isoformat(),
        }

    @classmethod
    def prepare_user_chats(cls, user_chats: list[Chat],
                           user_id: int,
                           ) -> UserChatsJSONDict:
        chats_for_json = []
        for chat in user_chats:
            try:
                last_message = cls.prepare_chat_message(chat.last_message)
            except IndexError:
                last_message = None
            chats_for_json.append({
                JSONKey.ID: chat.id,
                JSONKey.NAME: chat.define_chat_name_for_user_id(user_id=user_id),
                JSONKey.LAST_CHAT_MESSAGE: last_message,
            })
        return {JSONKey.CHATS: chats_for_json}
