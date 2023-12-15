from __future__ import annotations
from pydantic import BaseModel, constr, Field, EmailStr, ValidationError
from flask import request, abort
from http import HTTPStatus

from api.json_ import JSONKey

__all__ = (
    'RequestDataHandlerMixin',
    'UserJSONValidator',
)


class RequestDataHandlerMixin(BaseModel):
    """Базовый класс, позволяющий сразу получать провалидированные данные из запросов."""

    @classmethod
    def from_json(cls) -> RequestDataHandlerMixin | None:
        try:
            return cls(**request.json)
        except ValidationError:
            abort(HTTPStatus.BAD_REQUEST)


class UserJSONValidator(RequestDataHandlerMixin):
    """Модель для валидации JSON с данными для создания нового пользователя."""

    username: constr(min_length=1)
    password: constr(min_length=1)
    first_name: constr(min_length=1) = Field(alias=JSONKey.FIRST_NAME)
    last_name: constr(min_length=1) = Field(alias=JSONKey.LAST_NAME)
    email: EmailStr
    code: int
