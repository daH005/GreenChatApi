from functools import wraps
from http import HTTPStatus

from flask import request, abort

from common.json_keys import JSONKey
from db.models import MessageStorage
from http_.common.get_current_user import get_current_user

__all__ = (
    'check_permissions_decorator',
)


def check_permissions_decorator(func):
    @wraps(func)
    def wrapper():
        try:
            storage_id: int = int(request.args[JSONKey.STORAGE_ID])
        except (KeyError, ValueError):
            return abort(HTTPStatus.BAD_REQUEST)

        try:
            storage: MessageStorage = MessageStorage.by_id(storage_id)
        except ValueError:
            return abort(HTTPStatus.NOT_FOUND)

        if storage.message is None:
            return abort(HTTPStatus.FORBIDDEN)

        try:
            storage.message.chat.check_user_access(get_current_user().id)
        except PermissionError:
            return abort(HTTPStatus.FORBIDDEN)

        return func(storage)

    return wrapper
