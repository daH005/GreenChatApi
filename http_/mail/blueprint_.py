from flask import Blueprint, request, abort
from http import HTTPMethod, HTTPStatus
from typing import Literal
from pydantic import validate_email
from typing import Final
from random import randint

from api.http_.endpoints import EndpointName, Url
from api.json_ import JSONKey, CodeIsValidFlagJSONDict, JSONDictPreparer
from api.http_.redis_ import app as redis_app
from api.http_.mail.tasks import send_code_task

__all__ = (
    'bp',
    'make_and_save_code',
)

bp: Blueprint = Blueprint('mail', __name__)
REDIS_SET_NAME: Final[str] = 'greenchat_mail_codes'


def make_and_save_code() -> int:
    """Генерирует случайный код и сохраняет его в Redis.
    Гарантируется, что каждый новый код уникален.
    """
    code: int = randint(1000, 9999)
    if redis_app.sismember(REDIS_SET_NAME, str(code)):
        return make_and_save_code()
    redis_app.sadd(REDIS_SET_NAME, str(code))
    return code


def check_and_delete_code(code: int | str) -> None:
    """Проверяет наличие `code` в базе Redis.
    Если код имеется, то он удаляется. Если кода нет - вызывается `ValueError`.
    """
    if not redis_app.sismember(REDIS_SET_NAME, str(code)):
        raise ValueError
    redis_app.srem(REDIS_SET_NAME, str(code))


@bp.route(Url.SEND_CODE, endpoint=EndpointName.SEND_CODE, methods=[HTTPMethod.POST])
def send_code() -> dict[Literal['code'], int]:
    """Генерирует случайный код и отправляет его на указанную почту.
    Код сохраняется в Redis и хранится там до момента его подтверждения.
    Ожидается JSON с одним ключом - 'email'.
    """
    try:
        email: str = validate_email(request.json[JSONKey.EMAIL])[1]
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)
    code: int = make_and_save_code()
    send_code_task.delay(to=email, code=code)
    return dict(code=HTTPStatus.OK)


@bp.route(Url.CHECK_CODE, endpoint=EndpointName.CHECK_CODE, methods=[HTTPMethod.POST])
def check_code() -> CodeIsValidFlagJSONDict:
    """Проверяет код подтверждения почты. Возвращает словарь с флагом,
    обозначающим верен ли переданный код.
    Если код верен, то он удаляется из Redis.
    Ожидается JSON с одним ключом - 'code'.
    """
    try:
        code: int = int(request.json[JSONKey.CODE])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)
    try:
        check_and_delete_code(code)
    except ValueError:
        flag = False
    else:
        flag = True
    return JSONDictPreparer.prepare_code_is_valid(flag=flag)
