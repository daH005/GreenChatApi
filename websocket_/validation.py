from pydantic import BaseModel, Field, field_validator

from api.json_ import JSONKey
from api.websocket_.funcs import clear_message_text

__all__ = (
    'UserIdInfo',
    'NewChat',
    'NewChatMessage',
    'ChatIdInfo',
    'ChatMessageWasReadData',
)


class BaseModelWithTextField(BaseModel):
    text: str

    @field_validator('text')  # noqa: from pydantic doc
    @classmethod
    def _validate_text(cls, text: str) -> str:
        text = clear_message_text(text=text)
        if not text:
            raise AssertionError
        return text


class UserIdInfo(BaseModel):
    user_id: int = Field(alias=JSONKey.USER_ID)


class NewChat(BaseModelWithTextField):

    users_ids: list[int] = Field(alias=JSONKey.USERS_IDS)
    name: str | None = Field(default=None)
    is_group: bool = Field(alias=JSONKey.IS_GROUP, default=False)


class ChatIdInfo(BaseModel):
    chat_id: int = Field(alias=JSONKey.CHAT_ID)


class NewChatMessage(BaseModelWithTextField, ChatIdInfo):
    pass


class ChatMessageWasReadData(ChatIdInfo):
    chat_message_id: int = Field(alias=JSONKey.CHAT_MESSAGE_ID)
