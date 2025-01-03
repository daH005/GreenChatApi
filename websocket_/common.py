from re import sub
from typing import Final

from db.models import (
    UserChatMatch,
    User,
)
from websocket_.base.server import WebSocketServer

__all__ = (
    'TEXT_MAX_LENGTH',
    'clear_message_text',
    'user_ids_of_chat_by_id',
    'interlocutor_ids_for_user_by_id',
    'make_online_statuses_data',
)

TEXT_MAX_LENGTH: Final[int] = 10_000


def clear_message_text(text: str) -> str:
    text = text[:TEXT_MAX_LENGTH]
    text = sub(r' {2,}', ' ', text)
    text = sub(r'( ?\n ?)+', '\n', text)
    text = text.strip()
    return text


def user_ids_of_chat_by_id(chat_id: int) -> list[int]:
    return [user.id for user in UserChatMatch.users_of_chat(chat_id=chat_id)]


def interlocutor_ids_for_user_by_id(user_id: int) -> list[int]:
    interlocutors: list[User] = UserChatMatch.all_interlocutors_of_user(user_id=user_id)
    interlocutor_ids = [interlocutor.id for interlocutor in interlocutors]
    return interlocutor_ids


def make_online_statuses_data(server: WebSocketServer,
                              user_ids: list[int],
                              ) -> dict[int, bool]:
    result_data = {}
    for user_id in user_ids:
        if server.user_has_connections(user_id):
            result_data[user_id] = True

    return result_data
