from pydantic import BaseModel, Field, field_validator

from common.json_keys import JSONKey
from websocket_.common import clear_message_text

__all__ = (
    'UserIdJSONValidator',
    'NewChatJSONValidator',
    'NewChatMessageJSONValidator',
    'ChatIdJSONValidator',
    'ChatMessageWasReadJSONValidator',
)


class UserIdJSONValidator(BaseModel):
    user_id: int = Field(alias=JSONKey.USER_ID)


class NewChatJSONValidator(BaseModel):

    user_ids: list[int] = Field(alias=JSONKey.USER_IDS)
    name: str | None = Field(default=None)
    is_group: bool = Field(alias=JSONKey.IS_GROUP, default=False)


class ChatIdJSONValidator(BaseModel):
    chat_id: int = Field(alias=JSONKey.CHAT_ID)


class NewChatMessageJSONValidator(ChatIdJSONValidator):

    storage_id: int | None = Field(alias=JSONKey.STORAGE_ID, default=None)
    text: str

    @field_validator('text')  # noqa: from pydantic doc
    @classmethod
    def _validate_text(cls, text: str, values) -> str:
        if not text and not values.data.get('storage_id'):
            raise AssertionError
        return text


class ChatMessageWasReadJSONValidator(ChatIdJSONValidator):
    chat_message_id: int = Field(alias=JSONKey.CHAT_MESSAGE_ID)
