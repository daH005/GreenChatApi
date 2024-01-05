import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import create_session, Session
from datetime import datetime, timedelta

from api.db.encryption import make_auth_token
from api.db import models
from api.db.models import *
from common import make_random_string


USERS_PASSWORDS = {
    1: 'test_pass123',
    2: 'test_pass__',
    3: 'test_pass__',
    4: 'test_pass__44',
}

USERS = {
    1: User.new_by_password(
        'user1',
        USERS_PASSWORDS[1],
        'dan@mail.ru',
        'first_name',
        'last_name',
    ),
    2: User.new_by_password(
        'user2',
        USERS_PASSWORDS[2],
        'dan123@mail.ru',
        'first_name',
        'last_name',
    ),
    3: User.new_by_password(
        'dan005',
        USERS_PASSWORDS[3],
        'dan228@mail.ru',
        'first_name',
        'last_name',
    ),
    4: User.new_by_password(
        'new',
        USERS_PASSWORDS[4],
        'dan22811@mail.ru',
        'first_name',
        'last_name',
    ),
}

CHATS = {
    1: Chat(),
    2: Chat(),
    3: Chat(name='Беседа', is_group=True),
    4: Chat(name=None),
}

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
        user_id=2,
        chat_id=3,
    ),
    UserChatMatch(
        user_id=4,
        chat_id=2,
    ),
    UserChatMatch(
        user_id=4,
        chat_id=3,
    ),
]

INTERLOCUTOR_METHOD_ARGS_SETS = [
    (CHATS[1], USERS[1], USERS[2]),
    (CHATS[2], USERS[4], USERS[1]),
]

USER_CHATS_METHOD_ARGS_SETS = [
    (USERS[1], [
        CHATS[3],
        CHATS[2],
        CHATS[1],
    ]),
    (USERS[2], [
        CHATS[3],
        CHATS[1],
    ]),
    (USERS[4], [
        CHATS[3],
        CHATS[2],
    ]),
    (USERS[3], []),
]

USERS_IN_CHAT_METHOD_ARGS_SETS = [
    (CHATS[1], [USERS[1], USERS[2]]),
    (CHATS[3], [USERS[1], USERS[2], USERS[4]]),
    (CHATS[4], [])
]

CHAT_ACCESS_METHOD_ARGS_SETS = [
    (USERS[1], CHATS[1]),
    (USERS[1], CHATS[2]),
    (USERS[1], CHATS[3]),
    (USERS[2], CHATS[1]),
    (USERS[4], CHATS[2]),
]

NO_CHAT_ACCESS_METHOD_ARGS_SETS = [
    (USERS[1], CHATS[4]),
    (USERS[2], CHATS[4]),
    (USERS[2], CHATS[2]),
    (USERS[3], CHATS[1]),
    (USERS[3], CHATS[2]),
    (USERS[3], CHATS[3]),
    (USERS[3], CHATS[4]),
]

USERNAME_IS_ALREADY_TAKEN_METHOD_ARGS_SETS = [
    ('hi!111111111', False),
    (USERS[1].username, True),
    (USERS[2].username, True),
    (USERS[3].username, True),
    (USERS[4].username, True),
    ('new11', False),
]

EMAIL_IS_ALREADY_TAKEN_METHOD_ARGS_SETS = [
    ('hi!111111111@mail.ru', False),
    (USERS[1].email, True),
    (USERS[2].email, True),
    (USERS[3].email, True),
    (USERS[4].email, True),
    ('new11@yandex.ru', False),
]

FIND_PRIVATE_CHAT_METHOD_ARGS_SETS = [
    (USERS[1], USERS[2], CHATS[1]),
    (USERS[1], USERS[4], CHATS[2]),
]

NO_FIND_PRIVATE_CHAT_METHOD_ARGS_SETS = [
    (USERS[1], USERS[3]),
    (USERS[2], USERS[3]),
    (USERS[2], USERS[4]),
]

RANDOM_STRINGS = [make_random_string() for _ in range(10)]

TEXT_MESSAGES = [
    'hi!',
    'how are u?',
    '123123',
    '----',
    'Hi, my dear friend!\n'
    'It my letter for u....'
]


def _prepare_test_db() -> None:
    engine_for_test: Engine = create_engine('sqlite:///:memory:')

    session_for_test: Session = create_session(bind=engine_for_test)
    globals()['session'] = session_for_test
    models.session = session_for_test

    BaseModel.metadata.create_all(bind=engine_for_test)
    models.session.add_all([*USERS.values(), *CHATS.values(), *USERS_CHATS_MATCHES])  # type: ignore
    models.session.commit()

    # for exact `creating_datetime`:
    for message in CHATS_MESSAGES:
        models.session.add(message)
        models.session.commit()


class TestUser:

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
    def test_positive_user_has_required_attrs(attr_name: str) -> None:
        assert hasattr(User, attr_name)

    @staticmethod
    @pytest.mark.parametrize('user', USERS.values())
    def test_positive_user_has_encrypted_auth_token(user: User) -> None:
        assert user.auth_token == make_auth_token(user.username, USERS_PASSWORDS[user.id])

    @staticmethod
    @pytest.mark.parametrize('user', USERS.values())
    def test_positive_user_auth_by_username_and_password(user: User) -> None:
        assert User.auth_by_username_and_password(user.username, USERS_PASSWORDS[user.id]) == user

    @staticmethod
    @pytest.mark.parametrize(('username', 'password'), [(x, x) for x in RANDOM_STRINGS])
    def test_negative_user_auth_by_username_and_password_with_invalid_data_raises_value_error(username: str,
                                                                                              password: str,
                                                                                              ) -> None:
        with pytest.raises(ValueError):
            User.auth_by_username_and_password(username, password)

    @staticmethod
    @pytest.mark.parametrize('user', USERS.values())
    def test_positive_user_auth_by_token(user: User) -> None:
        assert User.auth_by_token(user.auth_token) == user

    @staticmethod
    @pytest.mark.parametrize('auth_token', RANDOM_STRINGS)
    def test_negative_user_auth_by_token_with_invalid_data_raises_value_error(auth_token: str) -> None:
        with pytest.raises(ValueError):
            User.auth_by_token(auth_token)

    @staticmethod
    @pytest.mark.parametrize(('username', 'flag'), USERNAME_IS_ALREADY_TAKEN_METHOD_ARGS_SETS)
    def test_positive_username_is_already_taken_flag(username: str,
                                                     flag: bool,
                                                     ) -> None:
        assert User.username_is_already_taken(username) == flag

    @staticmethod
    @pytest.mark.parametrize(('email', 'flag'), EMAIL_IS_ALREADY_TAKEN_METHOD_ARGS_SETS)
    def test_positive_email_is_already_taken_flag(email: str,
                                                  flag: bool,
                                                  ) -> None:
        assert User.email_is_already_taken(email) == flag


class TestChat:

    @staticmethod
    @pytest.mark.parametrize('attr_name', [
        'id',
        'name',
        'messages',
        'last_message',
        'interlocutor',
        'users',
    ])
    def test_positive_chat_has_required_attrs(attr_name: str) -> None:
        assert hasattr(Chat, attr_name)

    @staticmethod
    @pytest.mark.parametrize('chat', CHATS.values())
    def test_positive_last_message_is_last_added(chat: Chat) -> None:
        chat_message = ChatMessage(
            user_id=USERS[1].id,
            chat_id=chat.id,
            text='Hi!',
        )
        session.add(chat_message)
        session.commit()
        assert chat.last_message == chat_message
        session.delete(chat_message)
        session.commit()

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_user'), INTERLOCUTOR_METHOD_ARGS_SETS)
    def test_positive_interlocutor_definition(chat: Chat,
                                              user: User,
                                              expected_user: User,
                                              ) -> None:
        assert chat.interlocutor(user.id) == expected_user

    @staticmethod
    @pytest.mark.parametrize(('chat', 'expected_users'), USERS_IN_CHAT_METHOD_ARGS_SETS)
    def test_positive_users_in_chat(chat: Chat,
                                    expected_users: list[User],
                                    ) -> None:
        assert chat.users() == expected_users


class TestChatMessage:

    @staticmethod
    @pytest.mark.parametrize('attr_name', [
        'id',
        'user_id',
        'chat_id',
        'user',
        'text',
        'creating_datetime',
    ])
    def test_positive_chat_message_has_required_attrs(attr_name: str) -> None:
        assert hasattr(ChatMessage, attr_name)

    @staticmethod
    @pytest.mark.parametrize('text', TEXT_MESSAGES)
    def test_positive_creating_datetime_is_current_datetime(text: str) -> None:
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
    def test_positive_user_chat_match_has_required_attrs(attr_name: str) -> None:
        assert hasattr(UserChatMatch, attr_name)

    @staticmethod
    @pytest.mark.parametrize(('user', 'chat'), CHAT_ACCESS_METHOD_ARGS_SETS)
    def test_positive_chat_access(user: User,
                                  chat: Chat,
                                  ) -> None:
        assert UserChatMatch.chat_if_user_has_access(user.id, chat.id) == chat

    @staticmethod
    @pytest.mark.parametrize(('user', 'chat'), NO_CHAT_ACCESS_METHOD_ARGS_SETS)
    def test_negative_chat_not_access_and_raises_permission_error(user: User,
                                                                  chat: Chat,
                                                                  ) -> None:
        with pytest.raises(PermissionError):
            UserChatMatch.chat_if_user_has_access(user.id, chat.id)

    @staticmethod
    @pytest.mark.parametrize(('chat', 'expected_users'), USERS_IN_CHAT_METHOD_ARGS_SETS)
    def test_positive_users_in_chat(chat: Chat,
                                    expected_users: list[User],
                                    ) -> None:
        assert UserChatMatch.users_in_chat(chat.id) == expected_users

    @staticmethod
    @pytest.mark.parametrize(('user', 'expected_chats'), USER_CHATS_METHOD_ARGS_SETS)
    def test_positive_user_chats(user: User,
                                 expected_chats: list[Chat],
                                 ) -> None:
        assert UserChatMatch.user_chats(user.id) == expected_chats

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_user'), INTERLOCUTOR_METHOD_ARGS_SETS)
    def test_positive_interlocutor_definition(chat: Chat,
                                              user: User,
                                              expected_user: User,
                                              ) -> None:
        assert UserChatMatch.interlocutor(user.id, chat.id) == expected_user

    @staticmethod
    @pytest.mark.parametrize(('first_user', 'second_user', 'expected_chat'), FIND_PRIVATE_CHAT_METHOD_ARGS_SETS)
    def test_positive_find_private_chat(first_user: User,
                                        second_user: User,
                                        expected_chat: Chat,
                                        ) -> None:
        assert UserChatMatch.find_private_chat(first_user.id, second_user.id) == expected_chat

    @staticmethod
    @pytest.mark.parametrize(('first_user', 'second_user'), NO_FIND_PRIVATE_CHAT_METHOD_ARGS_SETS)
    def test_negative_find_private_chat_raises_value_error(first_user: User,
                                                           second_user: User,
                                                           ) -> None:
        with pytest.raises(ValueError):
            UserChatMatch.find_private_chat(first_user.id, second_user.id)


if __name__ in ('__main__', 'test_models'):
    _prepare_test_db()
