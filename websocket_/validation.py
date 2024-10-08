from pydantic import BaseModel, Field, field_validator

from common.json_ import JSONKey
from websocket_.common import clear_message_text

__all__ = (
    'TextJSONValidator',
    'UserIdJSONValidator',
    'NewChatJSONValidator',
    'NewChatMessageJSONValidator',
    'ChatIdJSONValidator',
    'ChatMessageWasReadJSONValidator',
)


class TextJSONValidator(BaseModel):
    text: str

    @field_validator('text')  # noqa: from pydantic doc
    @classmethod
    def _validate_text(cls, text: str) -> str:
        text = clear_message_text(text=text)
        if not text:
            raise AssertionError
        return text


class UserIdJSONValidator(BaseModel):
    user_id: int = Field(alias=JSONKey.USER_ID)


class NewChatJSONValidator(TextJSONValidator):

    users_ids: list[int] = Field(alias=JSONKey.USERS_IDS)
    name: str | None = Field(default=None)
    is_group: bool = Field(alias=JSONKey.IS_GROUP, default=False)


class ChatIdJSONValidator(BaseModel):
    chat_id: int = Field(alias=JSONKey.CHAT_ID)


class NewChatMessageJSONValidator(TextJSONValidator, ChatIdJSONValidator):
    pass


class ChatMessageWasReadJSONValidator(ChatIdJSONValidator):
    chat_message_id: int = Field(alias=JSONKey.CHAT_MESSAGE_ID)
