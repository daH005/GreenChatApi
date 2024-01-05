from re import sub
from typing import Final

from api.db.models import UserChatMatch

__all__ = (
    'UserID',
    'TEXT_MAX_LENGTH',
    'clear_text_message',
    'users_ids_of_chat_by_id',
)

UserID = int
TEXT_MAX_LENGTH: Final[int] = 10_000


def clear_text_message(text: str) -> str:
    text = text[:TEXT_MAX_LENGTH]
    text = sub(r' {2,}', ' ', text)
    text = sub(r'( ?\n ?)+', '\n', text)
    text = text.strip()
    return text


def users_ids_of_chat_by_id(chat_id: int) -> list[UserID]:
    return [user.id for user in UserChatMatch.users_in_chat(chat_id=chat_id)]


if __name__ == "__main__":
    print(clear_text_message(' string__    line-break\n\nnew-line\nnew-line-2\n'))
    print(clear_text_message('    '))
    print(clear_text_message(''))
    print(clear_text_message(' '))
