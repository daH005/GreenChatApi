from functools import wraps
from flask.sansio.scaffold import T_route
from flask import abort, request
from http import HTTPStatus

from api.db.models import User
from api.json_ import JSONKey

__all__ = (
    'auth_by_token_required',
)


def auth_by_token_required(route_func: T_route) -> T_route:
    """Добавляет к обработчику URL'а авторизацию по токену. Здесь ожидается заголовок 'authToken'.
    Если всё ок, то передаёт декорируемой функции параметр `auth_user`.
    """
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        # Валидация данных из заголовков + авторизация:
        try:
            auth_token: str = request.headers[JSONKey.AUTH_TOKEN]
            auth_user: User = User.auth_by_token(auth_token=auth_token)
        except (KeyError, ValueError):
            return abort(HTTPStatus.UNAUTHORIZED)
        # При успешной авторизации продолжаем выполнение декорируемого обработчика.
        return route_func(*args, **kwargs, auth_user=auth_user)
    return wrapper
