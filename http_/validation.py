from __future__ import annotations
from pydantic import (
    BaseModel,
    constr,
    Field,
    validate_email,
    field_validator,
    ValidationError,
)
from flask import request, abort
from http import HTTPStatus

from api.json_ import JSONKey

__all__ = (
    'RequestDataHandlerMixin',
    'UserJSONValidator',
)


class RequestDataHandlerMixin(BaseModel):

    @classmethod
    def from_json(cls) -> RequestDataHandlerMixin | None:
        try:
            return cls(**request.json)
        except ValidationError:
            abort(HTTPStatus.BAD_REQUEST)


class UserJSONValidator(RequestDataHandlerMixin):

    username: constr(min_length=5, max_length=100)
    password: constr(min_length=10, max_length=50)
    first_name: constr(min_length=1, max_length=100) = Field(alias=JSONKey.FIRST_NAME)
    last_name: constr(min_length=1, max_length=100) = Field(alias=JSONKey.LAST_NAME)
    email: constr(min_length=1, max_length=200)
    code: int

    @classmethod
    @field_validator('email')
    def email_validation(cls, email: str) -> str:
        return validate_email(email)[1]


if __name__ == '__main__':
    user = UserJSONValidator(
        username='dan005',
        password='sadasdsad12313',
        firstName='danil',
        lastName='yan',
        email='dan@mail.ru',
        code=123
    )
    from pprint import pprint
    pprint(user.model_dump())
