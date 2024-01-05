from pydantic import BaseModel, Field

from api.json_ import JSONKey

__all__ = (
    'NewChatMessage',
    'NewChat',
)


class NewChatMessage(BaseModel):

    chat_id: int = Field(alias=JSONKey.CHAT_ID)
    text: str


class NewChat(BaseModel):

    users_ids: list[int] = Field(alias=JSONKey.USERS_IDS)
    name: str
    is_group: bool = Field(alias=JSONKey.IS_GROUP)
