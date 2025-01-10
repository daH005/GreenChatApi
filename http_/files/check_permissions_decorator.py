from flask import request, abort
from http import HTTPStatus
from functools import wraps

from common.json_keys import JSONKey
from db.builder import db_builder
from db.models import ChatMessageStorage
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

        storage: ChatMessageStorage | None = db_builder.session.get(ChatMessageStorage, storage_id)
        if storage is None:
            return abort(HTTPStatus.NOT_FOUND)

        if storage.message is None:
            return abort(HTTPStatus.FORBIDDEN)

        try:
            storage.message.chat.check_user_access(get_current_user().id)
        except PermissionError:
            return abort(HTTPStatus.FORBIDDEN)

        return func(storage)

    return wrapper
