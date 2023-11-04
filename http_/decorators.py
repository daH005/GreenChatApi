from functools import wraps
from flask.sansio.scaffold import T_route
from flask import abort, request
from http import HTTPStatus

from db.models import User
from db.json_ import JSONKey

__all__ = (
    'auth_required',
)


def auth_required(route_func: T_route) -> T_route:
    """Добавляет к обработчику URL'а авторизацию. Здесь ожидается query-параметр 'authToken'.
    Если всё ок, то передаёт декорируемой функции параметр `auth_user`.
    """
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        # Валидация данных из query-параметров:
        try:
            auth_token: str = request.args[JSONKey.AUTH_TOKEN]
        except KeyError:
            return abort(HTTPStatus.BAD_REQUEST)
        # Авторизуем пользователя:
        try:
            auth_user: User = User.auth_by_token(auth_token=auth_token)
        except PermissionError:
            return abort(HTTPStatus.UNAUTHORIZED)
        # При успешной авторизации продолжаем выполнение декорируемого обработчика.
        return route_func(*args, **kwargs, auth_user=auth_user)
    return wrapper
