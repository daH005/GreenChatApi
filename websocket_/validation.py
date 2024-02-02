from pydantic import BaseModel, Field, field_validator

from api.json_ import JSONKey
from api.websocket_.funcs import clear_text_message

__all__ = (
    'NewInterlocutorOnlineStatusAdding',
    'NewChat',
    'NewChatMessage',
    'NewChatMessageTyping',
)


class BaseModelWithTextField(BaseModel):
    text: str

    @field_validator('text')  # noqa: from pydantic doc
    @classmethod
    def _validate_text(cls, text: str) -> str:
        text = clear_text_message(text=text)
        if not text:
            raise AssertionError
        return text


class NewInterlocutorOnlineStatusAdding(BaseModel):
    user_id: int = Field(alias=JSONKey.USER_ID)


class NewChat(BaseModelWithTextField):

    users_ids: list[int] = Field(alias=JSONKey.USERS_IDS)
    name: str | None = Field(default=None)
    is_group: bool = Field(alias=JSONKey.IS_GROUP, default=False)


class NewChatMessage(BaseModelWithTextField):
    chat_id: int = Field(alias=JSONKey.CHAT_ID)


class NewChatMessageTyping(BaseModel):
    chat_id: int = Field(alias=JSONKey.CHAT_ID)
