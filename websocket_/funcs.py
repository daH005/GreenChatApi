from re import sub
from typing import Final

from api.hinting import raises
from api.db.models import (
    session,
    UserChatMatch,
    ChatMessage,
)

__all__ = (
    'TEXT_MAX_LENGTH',
    'clear_text_message',
    'users_ids_of_chat_by_id',
    'make_chat_message_and_add_to_session',
)

TEXT_MAX_LENGTH: Final[int] = 10_000


def clear_text_message(text: str) -> str:
    text = text[:TEXT_MAX_LENGTH]
    text = sub(r' {2,}', ' ', text)
    text = sub(r'( ?\n ?)+', '\n', text)
    text = text.strip()
    return text


def users_ids_of_chat_by_id(chat_id: int) -> list[int]:
    return [user.id for user in UserChatMatch.users_in_chat(chat_id=chat_id)]


def make_chat_message_and_add_to_session(text: str,
                                         user_id: int,
                                         chat_id: int,
                                         ) -> ChatMessage:
    chat_message: ChatMessage = ChatMessage(
        user_id=user_id,
        chat_id=chat_id,
        text=text,
    )
    session.add(chat_message)
    return chat_message


if __name__ == "__main__":
    print(clear_text_message(' string__    line-break\n\nnew-line\nnew-line-2\n'))
    print(clear_text_message('    '))
    print(clear_text_message(''))
    print(clear_text_message(' '))
