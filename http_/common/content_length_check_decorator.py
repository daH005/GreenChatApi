from flask import request, abort
from http import HTTPStatus
from functools import wraps

__all__ = (
    'content_length_check_decorator',
)

_max_lengths: dict[str, int] = {}  # for tests


def content_length_check_decorator(max_length: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.content_length > _max_lengths[func.__name__]:
                return abort(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return func(*args, **kwargs)

        _max_lengths[func.__name__] = max_length
        return wrapper
    return decorator
