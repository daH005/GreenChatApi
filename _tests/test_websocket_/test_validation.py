import pytest
from pydantic import ValidationError
from typing import Final

# FixMe: Скорректировать после привязки БД.
from api import db
from api.websocket_.validation import AuthMessage, ChatMessage

# FixMe: Скорректировать после привязки БД.
USERS_FOR_TEST: Final[list] = [
    {
        'name': 'Danil',
    },
    {
        'name': 'Ivan',
    },
    {
        'name': 'Nicolay',
    }
]
# FixMe: Скорректировать после привязки БД.
CHATS_FOR_TEST: Final[list] = [
    {
        'messages': [],
        'users_ids': [0, 1]
    },
    {
        'messages': [],
        'users_ids': [2],
    }
]


def setup() -> None:
    """Формирует тестовые записи в тестовой БД."""
    # FixMe: Скорректировать после привязки БД.
    db.users.clear()
    db.users += USERS_FOR_TEST
    db.chats.clear()
    db.chats += CHATS_FOR_TEST


@pytest.mark.parametrize('user_id', range(len(USERS_FOR_TEST)))
def test_auth_message_ok_if_user_exist_and_auth(user_id: int) -> None:
    """Если пользователь существует и пароль верен, то всё должно быть ок."""
    AuthMessage(userId=user_id)


@pytest.mark.parametrize('user_id', [9999999, 123123123])
def test_auth_message_raises_if_user_not_exist(user_id: int) -> None:
    """Если пользователя не существует, то должен быть вызван `ValidationError`."""
    with pytest.raises(ValidationError):
        AuthMessage(userId=user_id)


@pytest.mark.skip('Сделать в будущем')
@pytest.mark.parametrize('user_id', [9999999, 123123123])
def test_auth_message_raises_if_user_exist_and_not_auth(user_id: int) -> None:
    """Если пароль не верен, то должен быть вызван `ValidationError`."""
    with pytest.raises(ValidationError):
        AuthMessage(userId=user_id)


@pytest.mark.parametrize(['user_id', 'chat_id'], [(0, 0), (1, 0), (2, 1)])
def test_chat_message_ok_if_user_in_chat(user_id: int,
                                         chat_id: int,
                                         ) -> None:
    """Если пользователь имеет доступ к чату, то всё должно быть ок."""
    ChatMessage(userId=user_id, chatId=chat_id, text='')


@pytest.mark.parametrize(['user_id', 'chat_id'], [(0, 1), (1, 1), (2, 0)])
def test_chat_message_raises_if_user_not_in_chat(user_id: int,
                                                 chat_id: int,
                                                 ) -> None:
    """Если пользователя не имеет доступа к чату, то должен быть вызван `ValidationError`."""
    with pytest.raises(ValidationError):
        ChatMessage(userId=user_id, chatId=chat_id, text='')


@pytest.mark.parametrize(['user_id', 'chat_id'], [(0, 99999), (1, 123123), (2, 100100)])
def test_chat_message_raises_if_chat_is_not_exist(user_id: int,
                                                  chat_id: int,
                                                  ) -> None:
    """Если пользователя пытается отправить сообщение в несуществующий чат, то должен быть вызван `ValidationError`."""
    with pytest.raises(ValidationError):
        ChatMessage(userId=user_id, chatId=chat_id, text='')
