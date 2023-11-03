from flask import Flask, request
from flask_cors import CORS
from http import HTTPMethod, HTTPStatus

from config import HOST, PORT
from api.db.models import User, UserChat
from api.db.json_ import ChatJSONDict

app: Flask = Flask(__name__)
# Важно! CORS позволяет обращаться к нашему rest api (http api) с других доменов / портов.
CORS(app)


@app.route('/chat_history', methods=[HTTPMethod.GET])
def chat_history() -> ChatJSONDict | tuple[str, HTTPStatus]:
    """Выдаёт всю историю заданного чата. Ожидаются query-параметры 'email', 'password' и 'chatId'."""
    # Валидация данных из query-параметров:
    try:
        email: str = request.args['email']
        password: str = request.args['password']
        chat_id: int = int(request.args['chatId'])
    except (ValueError, TypeError, KeyError):
        return 'Request data is invalid.', HTTPStatus.BAD_REQUEST
    # Авторизуем пользователя:
    try:
        auth_user: User = User.auth(email, password)
    except PermissionError:
        return 'Permission denied.', HTTPStatus.UNAUTHORIZED
    # Проверка доступа пользователя к заданному чату.
    # Если всё ок, то возвращаем историю.
    try:
        return UserChat.chat_if_user_has_access(auth_user.id, chat_id).to_json_dict()
    except PermissionError:
        return 'Permission denied or chat not found.', HTTPStatus.FORBIDDEN


if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)
