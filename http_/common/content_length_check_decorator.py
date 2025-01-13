from functools import wraps
from http import HTTPStatus

from flask import request, abort

__all__ = (
    'content_length_check_decorator',
)

_max_lengths: dict[str, int] = {}  # for tests


def content_length_check_decorator(max_length: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            content_length: int = request.content_length if request.content_length else 0
            if content_length > _max_lengths[func.__name__]:
                return abort(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return func(*args, **kwargs)

        _max_lengths[func.__name__] = max_length
        return wrapper
    return decorator
