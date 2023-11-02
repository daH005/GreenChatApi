from __future__ import annotations
from pydantic import (  # pip install pydantic
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

# FixMe: Скорректировать после привязки БД.
from api.db import users, chats

__all__ = (
    'ChatMessage',
    'AuthMessage',
)


class AuthMessage(BaseModel):
    """Первое сообщение от пользователя - авторизующее. Предполагает ID + пароль.
    Если пользователя под переданным `user_id` не существует,
    либо пароль не подходит, то вызывается `ValidationError`.
    """

    user_id: int = Field(alias='userId')

    @field_validator('user_id')  # noqa
    @classmethod
    def check_user_exist_and_auth(cls, user_id: int) -> int:
        # FixMe: Добавить проверку по паролю / токену / ключу сессии.
        # FixMe: Скорректировать после привязки БД.
        try:
            users[user_id]  # noqa
            return user_id
        except IndexError:
            raise AssertionError


class ChatMessage(BaseModel):
    """Рядовое сообщение от пользователя с `user_id` в чат `chat_id`.
    Попытка отправки сообщения в чат, недоступный пользователю, порождает `ValidationError`.
    """

    user_id: int = Field(alias='userId')
    chat_id: int = Field(alias='chatId')
    text: str

    @model_validator(mode='after')  # noqa
    @classmethod
    def check_chat_access(cls, message_: ChatMessage) -> ChatMessage:
        # FixMe: Скорректировать после привязки БД.
        try:
            chats[message_.chat_id]
        except IndexError:
            raise AssertionError
        assert message_.user_id in chats[message_.chat_id]['users_ids']
        return message_
