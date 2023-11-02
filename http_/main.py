from flask import Flask, request
from http import HTTPMethod, HTTPStatus
from pydantic import ValidationError

from config import HOST, PORT
# FixMe: Скорректировать после привязки БД.
from api.db import chats
from api.websocket_.validation import AuthMessage, ChatMessage

app: Flask = Flask(__name__)


# FixMe: Скорректировать после привязки БД.
@app.route('/chat_history', methods=[HTTPMethod.GET])
def chat_history() -> list[dict] | tuple[str, HTTPStatus]:
    """Выдаёт всю историю чата. Ожидаются query-параметры 'userId' и 'chatId'."""
    try:
        user_id: int = int(request.args.get('userId'))
        chat_id: int = int(request.args.get('chatId'))
    except (ValueError, TypeError):
        return 'Request data is invalid.', HTTPStatus.BAD_REQUEST
    try:
        AuthMessage(userId=user_id)
    except ValidationError:
        return 'Permission denied.', HTTPStatus.UNAUTHORIZED
    try:
        ChatMessage(userId=user_id,
                    chatId=chat_id,
                    text='',
                    )
    except ValidationError:
        return 'Permission denied or chat not found.', HTTPStatus.FORBIDDEN
    return chats[chat_id]['messages']


if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)
