import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import create_session, Session
from datetime import datetime, timedelta
from random import choice
from string import ascii_uppercase

from api.db.encryption import make_auth_token
from api.db import models
from api.db.models import *


def make_random_string() -> str:
    """Генерирует случайную 40-символьную строку. Число подобрано опытным путём."""
    return ''.join(choice(ascii_uppercase) for _ in range(40))


# Данные для создания тестовых пользователей.
NEW_USERS_TEST_DATA = [
    ('user1', 'test_pass123', 'dan@mail.ru'),  # id = 1
    ('user2', 'test_pass__', 'dan123@mail.ru'),  # id = 2
    ('dan005', 'test_pass__', 'dan228@mail.ru'),  # id = 3
]
# Данные для создания тестовых чатов.
NEW_CHATS_TEST_DATA = [
    None,  # id = 1
    None,  # id = 2
    'Беседа',  # id = 3
    None,  # id = 4
]
# Данные для создания тестовых сообщений.
NEW_CHATS_MESSAGES_TEST_DATA = [
    (1, 1, 'Hi!'),
    (2, 1, 'Hello! How are u?'),
    (1, 2, 'Yup.'),
    (1, 3, 'And?..'),
]
# Данные для создания тестовых доступов к чатам.
NEW_USERS_CHATS_MATCHES_TEST_DATA = [
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 1),
]


def _prepare_test_db() -> None:
    """Оформляет тестовую БД перед началом тестов.
    Подменяет объект сессии, а также создаёт таблицы.
    """
    engine_for_test: Engine = create_engine('sqlite:///:memory:')
    session_for_test: Session = create_session(bind=engine_for_test)
    globals()['session'] = session_for_test
    models.session = session_for_test
    BaseModel.metadata.create_all(bind=engine_for_test)


def _make_test_users() -> list[User]:
    """Создаёт и добавляет пользователей в тестовую БД."""
    users = []
    for user_data in NEW_USERS_TEST_DATA:
        user = User.new_by_password(
            username=user_data[0],
            password=user_data[1],
            email=user_data[2],
            first_name='first_name',
            last_name='last_name',
        )
        users.append(user)
        models.session.add(user)
    models.session.commit()
    return users


def _make_test_chats() -> list[Chat]:
    """Создаёт и добавляет чаты в тестовую БД."""
    chats = []
    for chat_data in NEW_CHATS_TEST_DATA:
        chat = Chat(
            name=chat_data,
        )
        chats.append(chat)
        models.session.add(chat)
    models.session.commit()
    return chats


def _make_test_chats_messages() -> list[ChatMessage]:
    """Создаёт и добавляет сообщения в тестовую БД."""
    chats_messages = []
    for chat_message_data in NEW_CHATS_MESSAGES_TEST_DATA:
        chat_message = ChatMessage(
            user_id=chat_message_data[0],
            chat_id=chat_message_data[1],
            text=chat_message_data[2],
        )
        chats_messages.append(chat_message)
        models.session.add(chat_message)
    models.session.commit()
    return chats_messages


def _make_test_users_chats_matches() -> list[UserChatMatch]:
    """Создаёт и добавляет доступы к чатам в тестовую БД."""
    users_chats_matches = []
    for user_chat_match_data in NEW_USERS_CHATS_MATCHES_TEST_DATA:
        user_chat_match = UserChatMatch(
            user_id=user_chat_match_data[0],
            chat_id=user_chat_match_data[1],
        )
        users_chats_matches.append(user_chat_match)
        models.session.add(user_chat_match)
    models.session.commit()
    return users_chats_matches


# Подготавливаем тестовую БД.
_prepare_test_db()
# Тестовые пользователи.
_TEST_USERS: list[User] = _make_test_users()
# Тестовые чаты.
_TEST_CHATS: list[Chat] = _make_test_chats()
# Тестовые сообщения.
_TEST_CHATS_MESSAGES: list[ChatMessage] = _make_test_chats_messages()
# Тестовые доступы.
_TEST_USERS_CHATS_MATCHES: list[UserChatMatch] = _make_test_users_chats_matches()


class TestUser:
    """Тестовый класс для модели пользователя."""

    @staticmethod
    @pytest.mark.parametrize('attr_name', [
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'auth_token',
        'new_by_password',
        'auth_by_username_and_password',
        'auth_by_token',
    ])
    def test_user_has_required_attrs(attr_name: str) -> None:
        """Позитивный тест: модель пользователя должна иметь необходимый перечень атрибутов."""
        assert hasattr(User, attr_name)

    @staticmethod
    @pytest.mark.parametrize('user', _TEST_USERS)
    def test_user_has_encrypted_auth_token(user: User) -> None:
        """Позитивный тест: пользователи должны иметь действительно зашифрованный токен авторизации."""
        assert user.auth_token == make_auth_token(user.username, NEW_USERS_TEST_DATA[user.id - 1][1])

    @staticmethod
    @pytest.mark.parametrize('user', _TEST_USERS)
    def test_user_auth_by_username_and_password(user: User) -> None:
        """Позитивный тест: авторизация по логину и паролю."""
        assert User.auth_by_username_and_password(user.username, NEW_USERS_TEST_DATA[user.id - 1][1]) == user

    @staticmethod
    @pytest.mark.parametrize(('username', 'password'),
                             [(make_random_string(), make_random_string()) for _ in range(10)])
    def test_user_auth_by_username_and_password_with_invalid_data_raises_value_error(username: str,
                                                                                     password: str,
                                                                                     ) -> None:
        """Негативный тест: авторизация по неверным логину или паролю должна вызывать `ValueError`."""
        with pytest.raises(ValueError):
            User.auth_by_username_and_password(username=username, password=password)

    @staticmethod
    @pytest.mark.parametrize('user', _TEST_USERS)
    def test_user_auth_by_token(user: User) -> None:
        """Позитивный тест: авторизация по токену."""
        assert User.auth_by_token(user.auth_token) == user

    @staticmethod
    @pytest.mark.parametrize('auth_token', [make_random_string() for _ in range(10)])
    def test_user_auth_by_token_with_invalid_data_raises_value_error(auth_token: str) -> None:
        """Негативный тест: авторизация по неверному токену должна вызывать `ValueError`."""
        with pytest.raises(ValueError):
            User.auth_by_token(auth_token)


class TestChat:
    """Тестовый класс для модели чата."""

    @staticmethod
    @pytest.mark.parametrize('attr_name', [
        'id',
        'name',
        'messages',
        'last_message',
    ])
    def test_chat_has_required_attrs(attr_name: str) -> None:
        """Позитивный тест: модель чата должна иметь необходимый перечень атрибутов."""
        assert hasattr(Chat, attr_name)

    @staticmethod
    @pytest.mark.parametrize('chat', _TEST_CHATS)
    def test_last_message_is_last_added(chat: Chat) -> None:
        """Позитивный тест: геттер `Chat.last_message` возвращает последний добавленный в БД `ChatMessage`."""
        chat_message = ChatMessage(
            user_id=_TEST_USERS[0].id,
            chat_id=chat.id,
            text='Hi!',
        )
        session.add(chat_message)
        session.commit()
        assert chat.last_message == chat_message
        session.delete(chat_message)
        session.commit()


class TestChatMessage:
    """Тестовый класс для модели сообщения."""

    @staticmethod
    @pytest.mark.parametrize('attr_name', [
        'id',
        'user_id',
        'chat_id',
        'user',
        'text',
        'creating_datetime',
    ])
    def test_chat_message_has_required_attrs(attr_name: str) -> None:
        """Позитивный тест: модель сообщения должна иметь необходимый перечень атрибутов."""
        assert hasattr(ChatMessage, attr_name)

    @staticmethod
    @pytest.mark.parametrize('text', ['hi', 'hello', 'how are u'])
    def test_creating_datetime_is_current_datetime(text: str) -> None:
        """Позитивный тест: дата и время создания сообщения соответствует действительности.
        Допускается разница в 10 миллисекунд в обе стороны.
        """
        chat_message = ChatMessage(
            user_id=1,
            chat_id=1,
            text=text,
        )
        session.add(chat_message)
        session.flush()
        max_datetime = datetime.utcnow() + timedelta(milliseconds=10)
        min_datetime = datetime.utcnow() - timedelta(milliseconds=10)
        assert max_datetime >= chat_message.creating_datetime >= min_datetime
        session.rollback()


class TestUserChatMatch:
    """Тестовый класс для модели доступа к чатам."""

    @staticmethod
    @pytest.mark.parametrize('attr_name', [
        'id',
        'user_id',
        'chat_id',
        'user',
        'chat',
        'chat_if_user_has_access',
        'users_in_chat',
        'user_chats',
        'chat_name',
    ])
    def test_user_chat_match_has_required_attrs(attr_name: str) -> None:
        """Позитивный тест: модель доступа к чату должна иметь необходимый перечень атрибутов."""
        assert hasattr(UserChatMatch, attr_name)

    @staticmethod
    @pytest.mark.parametrize(('user_id', 'chat_id'), [
        (1, 1),
        (2, 1),
        (1, 2),
        (1, 3),
    ])
    def test_chat_access(user_id: int,
                         chat_id: int,
                         ) -> None:
        """Позитивный тест: пользователь, состоящий в чате, должен иметь к нему доступ."""
        assert UserChatMatch.chat_if_user_has_access(user_id=user_id, chat_id=chat_id) == _TEST_CHATS[chat_id - 1]

    @staticmethod
    @pytest.mark.parametrize(('user_id', 'chat_id'), [
        (2, 2),
        (2, 3),
        (3, 1),
        (3, 2),
        (3, 3),
    ])
    def test_chat_not_access_and_raises_permission_error(user_id: int,
                                                         chat_id: int,
                                                         ) -> None:
        """Негативный тест: если пользователь пытается получить доступ к чату, в котором он не состоит,
        то вызывается `PermissionError`.
        """
        with pytest.raises(PermissionError):
            UserChatMatch.chat_if_user_has_access(user_id=user_id, chat_id=chat_id)

    @staticmethod
    @pytest.mark.parametrize(('chat_id', 'users'), [
        (1, [_TEST_USERS[0], _TEST_USERS[1]]),
        (2, [_TEST_USERS[0]]),
        (4, [])
    ])
    def test_users_in_chat(chat_id: int,
                           users: list[User],
                           ) -> None:
        """Позитивный тест: получение всех пользователей, состоящих в чате."""
        assert UserChatMatch.users_in_chat(chat_id=chat_id) == users

    @staticmethod
    @pytest.mark.parametrize(('user_id', 'chats'), [
        (1, _TEST_CHATS[:-1]),
        (2, [_TEST_CHATS[0]]),
        (3, []),
    ])
    def test_user_chats(user_id: int,
                        chats: list[Chat],
                        ) -> None:
        """Позитивный тест: получение всех чатов, в которых состоит пользователь."""
        assert UserChatMatch.user_chats(user_id=user_id) == chats

    @staticmethod
    @pytest.mark.parametrize(('user_id', 'chat_id', 'chat_name'), [
        (1, 1, _TEST_USERS[1].first_name),
        (1, 3, _TEST_CHATS[2].name),
    ])
    def test_chat_name(user_id: int,
                       chat_id: int,
                       chat_name: str,
                       ) -> None:
        """Позитивный тест: определение имени чата для конкретного пользователя.
        Если чат - это беседа, то выдаётся `Chat.name`, иначе - имя собеседника.
        """
        assert UserChatMatch.chat_name(user_id=user_id, chat_id=chat_id) == chat_name
