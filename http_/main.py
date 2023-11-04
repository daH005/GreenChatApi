from flask import Flask, request  # pip install flask
from flask_cors import CORS  # pip install -U flask-cors
from http import HTTPMethod, HTTPStatus

from config import HOST, PORT
from db.models import User, UserChat
from db.json_ import ChatJSONDict, JSONKey

app: Flask = Flask(__name__)
# Важно! CORS позволяет обращаться к нашему rest api (http api) с других доменов / портов.
CORS(app)


@app.route('/chat_history', methods=[HTTPMethod.GET])
def chat_history() -> ChatJSONDict | tuple[str, HTTPStatus]:
    """Выдаёт всю историю заданного чата. Ожидаются query-параметры 'authToken' и 'chatId'.
    При каждом обращении проверяет авторизацию пользователя по 'authToken'.
    """
    # Валидация данных из query-параметров:
    try:
        auth_token: str = request.args[JSONKey.AUTH_TOKEN]
        chat_id: int = int(request.args[JSONKey.CHAT_ID])
    except (ValueError, TypeError, KeyError):
        return 'Request data is invalid.', HTTPStatus.BAD_REQUEST
    # Авторизуем пользователя:
    try:
        auth_user: User = User.auth_by_token(auth_token=auth_token)
    except PermissionError:
        return 'Permission denied.', HTTPStatus.UNAUTHORIZED
    # Проверка доступа пользователя к заданному чату.
    # Если всё ок, то возвращаем историю.
    try:
        return UserChat.chat_if_user_has_access(
            user_id=auth_user.id,
            chat_id=chat_id,
        ).to_json_dict()
    except PermissionError:
        return 'Permission denied or chat not found.', HTTPStatus.FORBIDDEN


if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)
