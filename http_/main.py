from flask import Flask, request, abort  # pip install flask
from flask_cors import CORS  # pip install -U flask-cors
from http import HTTPMethod, HTTPStatus

from api.db.models import User, UserChatMatch
from api.json_ import (
    ChatJSONDict,
    UserChatsJSONDict,
    AuthTokenJSONDict,
    UserInfoJSONDict,
    JSONKey,
    JSONDictPreparer,
)
from api.config import HOST, HTTP_PORT as PORT
from endpoints import EndpointName, Url
from decorators import auth_by_token_required

app: Flask = Flask(__name__)
# Важно! CORS позволяет обращаться к нашему rest api (http api) с других доменов / портов.
CORS(app)


@app.route(Url.AUTH, endpoint=EndpointName.AUTH, methods=[HTTPMethod.POST])
def auth_by_username_and_password() -> AuthTokenJSONDict:
    """Авторизует пользователя по логину и паролю. Возвращает токен авторизации
    для его дальнейшего сохранение в cookie и работы с нашим rest api + websocket.
    """
    # Валидация данных из JSON:
    try:
        username: str = str(request.json[JSONKey.USERNAME])
        password: str = str(request.json[JSONKey.PASSWORD])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)
    # Проводим авторизацию.
    try:
        auth_user: User = User.auth_by_username_and_password(username, password)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)
    # Возвращаем токен для дальнейшего его сохранения у клиента в cookie.
    return JSONDictPreparer.auth_token(user=auth_user)


@app.route(Url.USER_INFO, endpoint=EndpointName.USER_INFO, methods=[HTTPMethod.GET])
@auth_by_token_required
def user_info(auth_user: User) -> UserInfoJSONDict:
    """Выдаёт всю информацию о пользователе (за исключением токена авторизации).
    При каждом обращении проверяет авторизацию по `authToken`.
    """
    return JSONDictPreparer.user_info(user=auth_user)


@app.route(Url.USER_CHATS, endpoint=EndpointName.USER_CHATS, methods=[HTTPMethod.GET])
@auth_by_token_required
def user_chats(auth_user: User) -> UserChatsJSONDict:
    """Выдаёт все чаты пользователя (от каждого чата берётся только последнее сообщение).
    Ожидается query-параметр 'authToken'.
    При каждом обращении проверяет авторизацию пользователя по 'authToken'.
    """
    return JSONDictPreparer.user_chats(
        user_chats=UserChatMatch.user_chats(user_id=auth_user.id),
        user=auth_user,
    )


@app.route(Url.CHAT_HISTORY, endpoint=EndpointName.CHAT_HISTORY, methods=[HTTPMethod.GET])
@auth_by_token_required
def chat_history(auth_user: User) -> ChatJSONDict:
    """Выдаёт всю историю заданного чата. Ожидаются query-параметры 'authToken' и 'chatId',
    а также опциональный параметр 'skipFromEndCount'.
    При каждом обращении проверяет авторизацию пользователя по 'authToken'.
    """
    # Валидация данных из query-параметров:
    try:
        chat_id: int = int(request.args[JSONKey.CHAT_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)
    # Параметр, определяющий отступ с конца истории.
    skip_from_end_count: int | None
    try:
        skip_from_end_count = int(request.args[JSONKey.SKIP_FROM_END_COUNT])
    except KeyError:
        skip_from_end_count = None
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)
    # Проверка доступа пользователя к заданному чату.
    # Если всё ок, то возвращаем историю.
    try:
        return JSONDictPreparer.chat_history(
            chat=UserChatMatch.chat_if_user_has_access(user_id=auth_user.id, chat_id=chat_id),
            skip_from_end_count=skip_from_end_count,
        )
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)


if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)
