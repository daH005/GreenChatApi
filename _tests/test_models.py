import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import create_session, Session
from datetime import datetime, timedelta

from api.db.encryption import make_auth_token
from api.db import models
from api.db.models import *
from common import make_random_string


# Пароли тестовых пользователей.
USERS_PASSWORDS = [
    'test_pass123',
    'test_pass__',
    'test_pass__',
    'test_pass__44',
]
# Тестовые пользователи.
USERS = [
    # id = 1
    User.new_by_password(
        username='user1',
        password=USERS_PASSWORDS[0],
        email='dan@mail.ru',
        first_name='first_name',
        last_name='last_name',
    ),
    # id = 2
    User.new_by_password(
        username='user2',
        password=USERS_PASSWORDS[1],
        email='dan123@mail.ru',
        first_name='first_name',
        last_name='last_name',
    ),
    # id = 3
    User.new_by_password(
        username='dan005',
        password=USERS_PASSWORDS[2],
        email='dan228@mail.ru',
        first_name='first_name',
        last_name='last_name',
    ),
    # id = 4
    User.new_by_password(
        username='new',
        password=USERS_PASSWORDS[3],
        email='dan22811@mail.ru',
        first_name='first_name',
        last_name='last_name',
    ),
]
# Тестовые чаты.
CHATS = [
    # id = 1
    Chat(name=None),
    # id = 2
    Chat(name=None),
    # id = 3
    Chat(name='Беседа'),
    # id = 4
    Chat(name=None),
]
# Тестовые сообщения.
CHATS_MESSAGES = [
    ChatMessage(
        user_id=1,
        chat_id=1,
        text='Hi!',
    ),
    ChatMessage(
        user_id=2,
        chat_id=1,
        text='Hello! How are u?',
    ),
    ChatMessage(
        user_id=1,
        chat_id=2,
        text='Yup.',
    ),
    ChatMessage(
        user_id=1,
        chat_id=3,
        text='And?..',
    ),
]
# Доступы к тестовым чатам.
USERS_CHATS_MATCHES = [
    UserChatMatch(
        user_id=1,
        chat_id=1,
    ),
    UserChatMatch(
        user_id=1,
        chat_id=2,
    ),
    UserChatMatch(
        user_id=1,
        chat_id=3,
    ),
    UserChatMatch(
        user_id=2,
        chat_id=1,
    ),
    UserChatMatch(
        user_id=4,
        chat_id=2,
    ),
]


def _prepare_test_db() -> None:
    """Оформляет тестовую БД перед началом тестов.
    Подменяет объект сессии, а также создаёт таблицы, после чего заполняет их
    объектами, определёнными в начале модуля.
    """
    engine_for_test: Engine = create_engine('sqlite:///:memory:')
    session_for_test: Session = create_session(bind=engine_for_test)
    globals()['session'] = session_for_test
    models.session = session_for_test
    BaseModel.metadata.create_all(bind=engine_for_test)
    models.session.add_all(USERS + CHATS + CHATS_MESSAGES + USERS_CHATS_MATCHES)  # type: ignore
    models.session.commit()


# Подготавливаем тестовую БД.
_prepare_test_db()


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
    @pytest.mark.parametrize('user', USERS)
    def test_user_has_encrypted_auth_token(user: User) -> None:
        """Позитивный тест: пользователи должны иметь действительно зашифрованный токен авторизации."""
        assert user.auth_token == make_auth_token(user.username, USERS_PASSWORDS[user.id - 1])

    @staticmethod
    @pytest.mark.parametrize('user', USERS)
    def test_user_auth_by_username_and_password(user: User) -> None:
        """Позитивный тест: авторизация по логину и паролю."""
        assert User.auth_by_username_and_password(user.username, USERS_PASSWORDS[user.id - 1]) == user

    @staticmethod
    @pytest.mark.parametrize(('username', 'password'),
                             [(make_random_string(), make_random_string()) for _ in range(10)])
    def test_user_auth_by_username_and_password_with_invalid_data_raises_value_error(username: str,
                                                                                     password: str,
                                                                                     ) -> None:
        """Негативный тест: авторизация по неверным логину или паролю должна вызывать `ValueError`."""
        with pytest.raises(ValueError):
            User.auth_by_username_and_password(username, password)

    @staticmethod
    @pytest.mark.parametrize('user', USERS)
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
        'interlocutor',
    ])
    def test_chat_has_required_attrs(attr_name: str) -> None:
        """Позитивный тест: модель чата должна иметь необходимый перечень атрибутов."""
        assert hasattr(Chat, attr_name)

    @staticmethod
    @pytest.mark.parametrize('chat', CHATS)
    def test_last_message_is_last_added(chat: Chat) -> None:
        """Позитивный тест: геттер `Chat.last_message` возвращает последний добавленный в БД `ChatMessage`."""
        chat_message = ChatMessage(
            user_id=USERS[0].id,
            chat_id=chat.id,
            text='Hi!',
        )
        session.add(chat_message)
        session.commit()
        assert chat.last_message == chat_message
        session.delete(chat_message)
        session.commit()

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user_id', 'expected_user'), [
        # Здесь ничего не перепутано!
        (CHATS[0], 1, USERS[1]),
        (CHATS[1], 4, USERS[0]),
    ])
    def test_interlocutor_definition(chat: Chat,
                                     user_id: int,
                                     expected_user: User,
                                     ) -> None:
        """Позитивный тест: определение собеседника пользователя в личном чате.
        Если чат - это беседа, то выдаётся `Chat.name`, иначе - имя собеседника.
        """
        assert chat.interlocutor(user_id) == expected_user


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
        'interlocutor',
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
        assert UserChatMatch.chat_if_user_has_access(user_id, chat_id) == CHATS[chat_id - 1]

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
            UserChatMatch.chat_if_user_has_access(user_id, chat_id)

    @staticmethod
    @pytest.mark.parametrize(('chat_id', 'expected_users'), [
        (1, [USERS[0], USERS[1]]),
        (2, [USERS[0], USERS[3]]),
        (4, [])
    ])
    def test_users_in_chat(chat_id: int,
                           expected_users: list[User],
                           ) -> None:
        """Позитивный тест: получение всех пользователей, состоящих в чате."""
        assert UserChatMatch.users_in_chat(chat_id) == expected_users

    @staticmethod
    @pytest.mark.parametrize(('user_id', 'expected_chats'), [
        # Чаты необходимо задавать в отсортированном виде по убыванию `Chat.last_message.creating_datetime`!
        (1, CHATS[:-1]),
        (2, [CHATS[0]]),
        (3, []),
    ])
    def test_user_chats(user_id: int,
                        expected_chats: list[Chat],
                        ) -> None:
        """Позитивный тест: получение всех чатов, в которых состоит пользователь.
        Чаты должны быть отсортированы по убыванию `Chat.last_message.creating_datetime`.
        """
        assert UserChatMatch.user_chats(user_id) == expected_chats

    @staticmethod
    @pytest.mark.parametrize(('user_id', 'chat_id', 'expected_user'), [
        # Здесь ничего не перепутано!
        (1, 1, USERS[1]),
        (2, 1, USERS[0]),
        (1, 2, USERS[3]),
    ])
    def test_interlocutor_definition(user_id: int,
                                     chat_id: int,
                                     expected_user: User,
                                     ) -> None:
        """Позитивный тест: определение имени собеседника.
        """
        assert UserChatMatch.interlocutor(user_id, chat_id) == expected_user
