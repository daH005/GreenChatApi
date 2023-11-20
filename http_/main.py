from flask import Flask, request, abort, Response  # pip install flask
from werkzeug.exceptions import HTTPException
from flask_cors import CORS  # pip install -U flask-cors
from http import HTTPMethod, HTTPStatus
from json import dumps as json_dumps

from api.db.models import User, UserChatMatch, session
from api.json_ import (
    ChatHistoryJSONDict,
    UserChatsJSONDict,
    AuthTokenJSONDict,
    UserInfoJSONDict,
    JSONKey,
    JSONDictPreparer,
)
from api.config import HOST, HTTP_PORT as PORT, CORS_ORIGINS
from endpoints import EndpointName, Url
from decorators import auth_by_token_required

app: Flask = Flask(__name__)
# Важно! CORS позволяет обращаться к нашему REST api с других доменов / портов.
CORS(app, origins=CORS_ORIGINS)


@app.teardown_appcontext
def shutdown_db_session(exception=None) -> None:  # noqa
    """Закрывает сессию БД после выполнения обработки запроса."""
    session.remove()


@app.errorhandler(HTTPException)
def handle_exception(exception: HTTPException) -> Response:
    """Заменяет все HTML-представления статус-кодов на JSON."""
    response = exception.get_response()
    response.content_type = 'application/json'
    response.data = json_dumps(dict(code=exception.code))
    return response


@app.route(Url.AUTH, endpoint=EndpointName.AUTH, methods=[HTTPMethod.POST])
def auth_by_username_and_password() -> AuthTokenJSONDict:
    """Авторизует пользователя по логину и паролю. Возвращает токен авторизации
    для его дальнейшего сохранения в cookie и работы с нашим RESTful api + websocket.
    Ожидается JSON с ключами 'username' и 'password'.
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
    except ValueError:
        return abort(HTTPStatus.FORBIDDEN)
    # Возвращаем токен для дальнейшего его сохранения у клиента в cookie.
    return JSONDictPreparer.prepare_auth_token(auth_token=auth_user.auth_token)


@app.route(Url.USER_INFO, endpoint=EndpointName.USER_INFO, methods=[HTTPMethod.GET])
@auth_by_token_required
def user_info(auth_user: User) -> UserInfoJSONDict:
    """Выдаёт всю информацию о `auth_user` (за исключением токена авторизации).
    Ожидается заголовок 'authToken'.
    """
    return JSONDictPreparer.prepare_user_info(user=auth_user, exclude_important_info=False)


@app.route(Url.USER_CHATS, endpoint=EndpointName.USER_CHATS, methods=[HTTPMethod.GET])
@auth_by_token_required
def user_chats(auth_user: User) -> UserChatsJSONDict:
    """Выдаёт все чаты `auth_user` (от каждого чата берётся только последнее сообщение).
    Ожидается заголовок 'authToken'.
    """
    return JSONDictPreparer.prepare_user_chats(
        user_chats=UserChatMatch.user_chats(user_id=auth_user.id),
        user_id=auth_user.id,
    )


@app.route(Url.CHAT_HISTORY, endpoint=EndpointName.CHAT_HISTORY, methods=[HTTPMethod.GET])
@auth_by_token_required
def chat_history(chat_id: int,
                 auth_user: User,
                 ) -> ChatHistoryJSONDict:
    """Выдаёт всю историю заданного чата (при условии, что он доступен для `auth_user`).
    Ожидается заголовок 'authToken', а также опциональный query-параметр 'offsetFromEnd'.
    """
    # Параметр, определяющий отступ с конца истории.
    offset_from_end: int | None
    try:
        offset_from_end = -int(request.args[JSONKey.OFFSET_FROM_END])
    except KeyError:
        offset_from_end = None
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)
    # Проверка доступа пользователя к заданному чату.
    # Если всё ок, то возвращаем историю.
    try:
        return JSONDictPreparer.prepare_chat_history(
            chat_messages=UserChatMatch.chat_if_user_has_access(user_id=auth_user.id,
                                                                chat_id=chat_id).messages[:offset_from_end],
        )
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)


if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)
