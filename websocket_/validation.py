from pydantic import BaseModel, Field

from api.json_ import JSONKey

__all__ = (
    'NewChat',
    'NewChatMessage',
    'NewChatTypingMessage',
)


class NewChat(BaseModel):

    users_ids: list[int] = Field(alias=JSONKey.USERS_IDS)
    name: str | None = Field(default=None)
    is_group: bool = Field(alias=JSONKey.IS_GROUP, default=False)
    text: str


class NewChatMessage(BaseModel):

    chat_id: int = Field(alias=JSONKey.CHAT_ID)
    text: str


class NewChatTypingMessage(BaseModel):
    chat_id: int = Field(alias=JSONKey.CHAT_ID)
