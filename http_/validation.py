from __future__ import annotations
from pydantic import (
    BaseModel,
    constr,
    conint,
    validate_email,
    field_validator,
    ValidationError,
)
from flask import request, abort
from http import HTTPStatus

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

    email: constr(min_length=1, max_length=200)
    code: conint(ge=1000)

    @field_validator('email')  # noqa: from pydantic doc
    @classmethod
    def _validate_email(cls, data: str) -> str:
        return validate_email(data)[1]
