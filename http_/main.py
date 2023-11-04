from flask import Flask, request, abort  # pip install flask
from flask_cors import CORS  # pip install -U flask-cors
from http import HTTPMethod, HTTPStatus

from db.models import User, UserChat
from db.json_ import SomeChatMessagesJSONDict, JSONKey
from config import HOST, PORT
from endpoints import EndpointName, Url
from decorators import auth_required

app: Flask = Flask(__name__)
# Важно! CORS позволяет обращаться к нашему rest api (http api) с других доменов / портов.
CORS(app)


@app.route(Url.CHAT_HISTORY, endpoint=EndpointName.CHAT_HISTORY, methods=[HTTPMethod.GET])
@auth_required
def chat_history(auth_user: User) -> SomeChatMessagesJSONDict:
    """Выдаёт всю историю заданного чата. Ожидаются query-параметры 'authToken' и 'chatId'.
    При каждом обращении проверяет авторизацию пользователя по 'authToken'.
    """
    # Валидация данных из query-параметров:
    try:
        chat_id: int = int(request.args[JSONKey.CHAT_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)
    # Проверка доступа пользователя к заданному чату.
    # Если всё ок, то возвращаем историю.
    try:
        return UserChat.chat_if_user_has_access(
            user_id=auth_user.id,
            chat_id=chat_id,
        ).to_json_dict()
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)


@app.route(Url.ALL_LAST_CHATS_MESSAGES, endpoint=EndpointName.ALL_LAST_CHATS_MESSAGES, methods=[HTTPMethod.GET])
@auth_required
def all_last_chats_messages(auth_user: User) -> SomeChatMessagesJSONDict:
    """Выдаёт последние сообщения всех чатов пользователя. Ожидается query-параметр 'authToken'.
    При каждом обращении проверяет авторизацию пользователя по 'authToken'.
    """
    return UserChat.all_last_chats_messages_json_dict(user_id=auth_user.id)


if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)
