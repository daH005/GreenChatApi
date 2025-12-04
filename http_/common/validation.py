from http import HTTPStatus
from re import sub
from typing import Union, Final

from flask import request, abort
from pydantic import (
    BaseModel,
    constr,
    conint,
    validate_email,
    field_validator,
    ValidationError,
    Field,
)

from common.json_keys import JSONKey

__all__ = (
    'BaseValidator',
    'EmailAndCodeJSONValidator',
    'UserJSONValidator',
    'EditMessageJSONValidator',
    'NewChatJSONValidator',
    'NewMessageJSONValidator',
    'FilenamesJSONValidator',
    'OffsetSizeJSONValidator',
)


class BaseValidator(BaseModel):

    @classmethod
    def from_json(cls) -> Union['BaseValidator', None]:
        return cls._from('json')

    @classmethod
    def from_args(cls) -> Union['BaseValidator', None]:
        return cls._from('args')

    @classmethod
    def _from(cls, attr_name: str) -> Union['BaseValidator', None]:
        try:
            return cls(**getattr(request, attr_name))
        except ValidationError:
            abort(HTTPStatus.BAD_REQUEST)


class EmailAndCodeJSONValidator(BaseValidator):

    email: constr(min_length=1, max_length=200)
    code: conint(ge=1000, le=9999)

    @field_validator('email')  # noqa: from pydantic doc
    @classmethod
    def _validate_email(cls, data: str) -> str:
        return validate_email(data)[1]


class UserJSONValidator(BaseValidator):

    first_name: constr(min_length=1, max_length=20) = Field(alias=JSONKey.FIRST_NAME)
    last_name: constr(min_length=1, max_length=20) = Field(alias=JSONKey.LAST_NAME)


class NewChatJSONValidator(BaseValidator):

    user_ids: list[int] = Field(alias=JSONKey.USER_IDS, min_length=1)
    name: str | None = Field(default=None)
    is_group: bool = Field(alias=JSONKey.IS_GROUP, default=False)


class BaseMessageJSONValidator(BaseValidator):
    _TEXT_MAX_LENGTH: Final[int] = 10_000

    replied_message_id: int = Field(alias=JSONKey.REPLIED_MESSAGE_ID, default=None)
    text: str = Field(alias=JSONKey.TEXT, default=None)

    @field_validator('text')  # noqa: from pydantic doc
    @classmethod
    def _validate_text(cls, text: str) -> str:
        text = _cls.clear_text(text)
        if not text:
            raise AssertionError
        return text

    @classmethod
    def _clear_text(cls, text: str) -> str:
        text = text[:cls._TEXT_MAX_LENGTH]
        text = sub(r' {2,}', ' ', text)
        text = sub(r'( ?\n ?)+', '\n', text)
        text = text.strip()
        return text


class NewMessageJSONValidator(BaseMessageJSONValidator):

    chat_id: int = Field(alias=JSONKey.CHAT_ID)
    text: str = Field(alias=JSONKey.TEXT)


class EditMessageJSONValidator(BaseMessageJSONValidator):
    message_id: int = Field(alias=JSONKey.MESSAGE_ID)


class FilenamesJSONValidator(BaseValidator):
    filenames: list[str] = Field(alias=JSONKey.FILENAMES)


class OffsetSizeJSONValidator(BaseValidator):

    offset: int = Field(alias=JSONKey.OFFSET, ge=0, default=0)
    size: int = Field(alias=JSONKey.SIZE, ge=1, le=100, default=20)
