from flask import request, abort
from http import HTTPStatus
from functools import wraps
from typing import Union

from common.hinting import raises
from common.json_keys import JSONKey
from db.exceptions import (
    DBEntityNotFoundException,
    DBEntityIsForbiddenException,
)
from db.models import (
    BaseModel,
    Chat,
    Message,
    User,
)
from http_.common.get_current_user import get_current_user

__all__ = (
    'message_access_query_decorator',
    'message_access_json_decorator',
    'message_full_access_query_decorator',
    'message_full_access_json_decorator',
    'chat_access_query_decorator',
    'chat_access_json_decorator',
)


def message_access_query_decorator(func):
    return _message_access_decorator(
        func, _get_id_from_query,
    )


def message_access_json_decorator(func):
    return _message_access_decorator(
        func, _get_id_from_json,
    )


def message_full_access_query_decorator(func):
    return _message_full_access_decorator(
        func, _get_id_from_query,
    )


def message_full_access_json_decorator(func):
    return _message_full_access_decorator(
        func, _get_id_from_json,
    )


def chat_access_query_decorator(func):
    return _chat_access_decorator(
        func, _get_id_from_query,
    )


def chat_access_json_decorator(func):
    return _chat_access_decorator(
        func, _get_id_from_json,
    )


def _message_access_decorator(func,
                              get_id_func: Union['_get_id_from_query', '_get_id_from_json'],
                              ):
    return _abstract_access_decorator(
        func,
        get_id_func,
        JSONKey.MESSAGE_ID,
        Message,
        _message_access_checking,
    )


def _message_full_access_decorator(func,
                                   get_id_func: Union['_get_id_from_query', '_get_id_from_json'],
                                   ):
    return _abstract_access_decorator(
        func,
        get_id_func,
        JSONKey.MESSAGE_ID,
        Message,
        _message_full_access_checking,
    )


def _chat_access_decorator(func,
                           get_id_func: Union['_get_id_from_query', '_get_id_from_json'],
                           ):
    return _abstract_access_decorator(
        func,
        get_id_func,
        JSONKey.CHAT_ID,
        Chat,
        _chat_access_checking,
    )


def _abstract_access_decorator(func,
                               get_id_func: Union['_get_id_from_query', '_get_id_from_json'],
                               key: str,
                               model: type[BaseModel],
                               check_access_func: Union['_chat_access_checking', '_message_access_checking'],
                               ):
    @wraps(func)
    def wrapper():
        try:
            entity_id: int = get_id_func(key)
        except (ValueError, KeyError):
            return abort(HTTPStatus.BAD_REQUEST)

        try:
            entity = model.by_id(entity_id)
        except DBEntityNotFoundException:
            return abort(HTTPStatus.NOT_FOUND)

        user: User = get_current_user()
        try:
            check_access_func(entity, user.id)
        except DBEntityIsForbiddenException:
            return abort(HTTPStatus.FORBIDDEN)

        return func(entity, user)

    return wrapper


@raises(KeyError, ValueError)
def _get_id_from_query(key: str) -> int:
    return int(request.args[key])


@raises(KeyError, ValueError)
def _get_id_from_json(key: str) -> int:
    return int(request.json[key])


@raises(DBEntityIsForbiddenException)
def _chat_access_checking(chat: Chat,
                          user_id: int,
                          ) -> None:
    chat.check_user_access(user_id)


@raises(DBEntityIsForbiddenException)
def _message_access_checking(message: Message,
                             user_id: int,
                             ) -> None:
    message.chat.check_user_access(user_id)


@raises(DBEntityIsForbiddenException)
def _message_full_access_checking(message: Message,
                                  user_id: int,
                                  ) -> None:
    _message_access_checking(message, user_id)
    if message.user.id != user_id:
        raise DBEntityIsForbiddenException
