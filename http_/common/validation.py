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
    'NewChatJSONValidator',
    'NewMessageJSONValidator',
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


class NewMessageJSONValidator(BaseValidator):
    _TEXT_MAX_LENGTH: Final[int] = 10_000

    chat_id: int = Field(alias=JSONKey.CHAT_ID)
    text: str = Field(alias=JSONKey.TEXT)

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
