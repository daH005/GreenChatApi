from __future__ import annotations
from pydantic import (
    BaseModel,
    constr,
    conint,
    validate_email,
    field_validator,
    ValidationError,
    Field,
)
from flask import request, abort
from http import HTTPStatus

from api.common.json_ import JSONKey

__all__ = (
    'BaseValidator',
    'EmailAndCodeJSONValidator',
    'UserJSONValidator',
)


class BaseValidator(BaseModel):

    @classmethod
    def from_json(cls) -> BaseValidator | None:
        return cls._from('json')

    @classmethod
    def from_args(cls) -> BaseValidator | None:
        return cls._from('args')

    @classmethod
    def _from(cls, attr_name: str) -> BaseValidator | None:
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
