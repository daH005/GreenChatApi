from pydantic import BaseModel, Field, field_validator
from typing import Final
from re import sub

from common.json_keys import JSONKey

__all__ = (
    'UserIdJSONValidator',
    'NewChatJSONValidator',
    'NewMessageJSONValidator',
    'ChatIdJSONValidator',
    'MessageWasReadJSONValidator',
)


class UserIdJSONValidator(BaseModel):
    user_id: int = Field(alias=JSONKey.USER_ID)


class NewChatJSONValidator(BaseModel):

    user_ids: list[int] = Field(alias=JSONKey.USER_IDS)
    name: str | None = Field(default=None)
    is_group: bool = Field(alias=JSONKey.IS_GROUP, default=False)


class ChatIdJSONValidator(BaseModel):
    chat_id: int = Field(alias=JSONKey.CHAT_ID)


class NewMessageJSONValidator(ChatIdJSONValidator):
    _TEXT_MAX_LENGTH: Final[int] = 10_000

    storage_id: int | None = Field(alias=JSONKey.STORAGE_ID, default=None)
    text: str

    @field_validator('text')  # noqa: from pydantic doc
    @classmethod
    def _validate_text(cls, text: str, values) -> str:
        if not text and not values.data.get('storage_id'):
            raise AssertionError
        return cls.clear_text(text)

    @classmethod
    def clear_text(cls, text: str) -> str:
        text = text[:cls._TEXT_MAX_LENGTH]
        text = sub(r' {2,}', ' ', text)
        text = sub(r'( ?\n ?)+', '\n', text)
        text = text.strip()
        return text


class MessageWasReadJSONValidator(ChatIdJSONValidator):
    message_id: int = Field(alias=JSONKey.MESSAGE_ID)
