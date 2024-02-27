import pytest
from datetime import datetime, timedelta

from api._tests.all_test_data.db_test_data import *  # noqa: must be first!
from api.db.encryption import make_auth_token
from api.db.models import *  # noqa


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
    @pytest.mark.parametrize(('username', 'flag'), ALREADY_TAKEN_AND_NOT_USERNAMES)
    def test_positive_username_is_already_taken_flag(username: str,
                                                     flag: bool,
                                                     ) -> None:
        assert User.username_is_already_taken(username) == flag

    @staticmethod
    @pytest.mark.parametrize(('email', 'flag'), ALREADY_TAKEN_AND_NOT_EMAILS)
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
        session.refresh(chat)  # important
        assert chat.last_message == chat_message
        session.delete(chat_message)
        session.commit()

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_user'), CHATS_INTERLOCUTORS)
    def test_positive_interlocutor_definition(chat: Chat,
                                              user: User,
                                              expected_user: User,
                                              ) -> None:
        assert chat.interlocutor(user.id) == expected_user

    @staticmethod
    @pytest.mark.parametrize(('chat', 'expected_users'), USERS_IN_CHATS)
    def test_positive_users_in_chat(chat: Chat,
                                    expected_users: list[User],
                                    ) -> None:
        assert set(chat.users()) == set(expected_users)


class TestChatMessage:

    @staticmethod
    @pytest.mark.parametrize('attr_name', [
        'id',
        'user_id',
        'chat_id',
        'user',
        'text',
        'creating_datetime',
        'is_read',
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
    @pytest.mark.parametrize(('user', 'chat'), CHATS_ACCESS_FOR_USERS)
    def test_positive_chat_access(user: User,
                                  chat: Chat,
                                  ) -> None:
        assert UserChatMatch.chat_if_user_has_access(user.id, chat.id) == chat

    @staticmethod
    @pytest.mark.parametrize(('user', 'chat'), CHATS_NO_ACCESS_FOR_USERS)
    def test_negative_chat_not_access_and_raises_permission_error(user: User,
                                                                  chat: Chat,
                                                                  ) -> None:
        with pytest.raises(PermissionError):
            UserChatMatch.chat_if_user_has_access(user.id, chat.id)

    @staticmethod
    @pytest.mark.parametrize(('chat', 'expected_users'), USERS_IN_CHATS)
    def test_positive_users_in_chat(chat: Chat,
                                    expected_users: list[User],
                                    ) -> None:
        assert set(UserChatMatch.users_in_chat(chat.id)) == set(expected_users)

    @staticmethod
    @pytest.mark.parametrize(('user', 'expected_chats'), USERS_CHATS)
    def test_positive_user_chats(user: User,
                                 expected_chats: list[Chat],
                                 ) -> None:
        assert UserChatMatch.user_chats(user.id) == expected_chats

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_user'), CHATS_INTERLOCUTORS)
    def test_positive_interlocutor_definition(chat: Chat,
                                              user: User,
                                              expected_user: User,
                                              ) -> None:
        assert UserChatMatch.interlocutor(user.id, chat.id) == expected_user

    @staticmethod
    @pytest.mark.parametrize(('first_user', 'second_user', 'expected_chat'), PRIVATE_CHATS_USERS)
    def test_positive_find_private_chat(first_user: User,
                                        second_user: User,
                                        expected_chat: Chat,
                                        ) -> None:
        assert UserChatMatch.find_private_chat(first_user.id, second_user.id) == expected_chat

    @staticmethod
    @pytest.mark.parametrize(('first_user', 'second_user'), USERS_WITHOUT_PRIVATE_CHAT)
    def test_negative_find_private_chat_raises_value_error(first_user: User,
                                                           second_user: User,
                                                           ) -> None:
        with pytest.raises(ValueError):
            UserChatMatch.find_private_chat(first_user.id, second_user.id)

    @staticmethod
    @pytest.mark.parametrize(('user', 'expected_users'), ALL_INTERLOCUTORS_OF_USERS)
    def test_positive_find_all_interlocutors(user: User,
                                             expected_users: list[User],
                                             ) -> None:
        assert set(UserChatMatch.find_all_interlocutors(user.id)) == set(expected_users)
