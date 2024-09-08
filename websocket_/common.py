from re import sub
from typing import Final

from api.db.models import (
    UserChatMatch,
    ChatMessage,
    User,
)
from api.db.builder import db_builder
from api.websocket_.base.server import WebSocketServer

__all__ = (
    'TEXT_MAX_LENGTH',
    'clear_message_text',
    'users_ids_of_chat_by_id',
    'make_chat_message_and_add_to_session',
    'interlocutors_ids_for_user_by_id',
    'make_online_statuses_data',
)

TEXT_MAX_LENGTH: Final[int] = 10_000


def clear_message_text(text: str) -> str:
    text = text[:TEXT_MAX_LENGTH]
    text = sub(r' {2,}', ' ', text)
    text = sub(r'( ?\n ?)+', '\n', text)
    text = text.strip()
    return text


def users_ids_of_chat_by_id(chat_id: int) -> list[int]:
    return [user.id for user in UserChatMatch.users_of_chat(chat_id=chat_id)]


def make_chat_message_and_add_to_session(text: str,
                                         user_id: int,
                                         chat_id: int,
                                         ) -> ChatMessage:
    chat_message: ChatMessage = ChatMessage(
        user_id=user_id,
        chat_id=chat_id,
        text=text,
    )
    db_builder.session.add(chat_message)
    return chat_message


def interlocutors_ids_for_user_by_id(user_id: int) -> list[int]:
    interlocutors: list[User] = UserChatMatch.all_interlocutors_of_user(user_id=user_id)
    interlocutors_ids = [interlocutor.id for interlocutor in interlocutors]
    return interlocutors_ids


def make_online_statuses_data(server: WebSocketServer,
                              users_ids: list[int],
                              ) -> dict[int, bool]:
    result_data = {}
    for user_id in users_ids:
        if server.user_have_connections(user_id):
            result_data[user_id] = True

    return result_data
