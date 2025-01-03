import pytest

from db.models import (
    User,
    Chat,
    ChatMessage,
    UserChatMatch,
)
from _tests.data.models import ORMObjects, SetForTest
from _tests.common.create_test_db import create_test_db


def setup_module() -> None:
    create_test_db(ORMObjects.all)


class TestUser:

    @staticmethod
    @pytest.mark.parametrize(('email', 'expected_user'), SetForTest.User.by_email)
    def test_by_email(email: str,
                      expected_user: User,
                      ) -> None:
        assert User.by_email(email) == expected_user

    @staticmethod
    @pytest.mark.parametrize(('email', 'expected_flag'), SetForTest.User.email_is_already_taken)
    def test_email_is_already_taken(email: str,
                                    expected_flag: bool,
                                    ) -> None:
        assert User.email_is_already_taken(email) == expected_flag

    @staticmethod
    @pytest.mark.parametrize(('user', 'expected_chats'), SetForTest.User.chats)
    def test_chats(user: User,
                   expected_chats: list[Chat],
                   ) -> None:
        assert user.chats() == expected_chats


class TestChat:

    @staticmethod
    @pytest.mark.parametrize(('chat', 'expected_users'), SetForTest.Chat.users)
    def test_users(chat: Chat,
                   expected_users: list[User],
                   ) -> None:
        assert chat.users() == expected_users

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user'), SetForTest.Chat.check_user_access)
    def test_check_user_access(chat: Chat,
                               user: User,
                               ) -> None:
        chat.check_user_access(user.id)

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user'), SetForTest.Chat.check_user_access_raises_permission_error)
    def test_check_user_access_raises_permission_error(chat: Chat,
                                                       user: User,
                                                       ) -> None:
        with pytest.raises(PermissionError):
            chat.check_user_access(user.id)

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_messages'), SetForTest.Chat.unread_messages_of_user)
    def test_unread_messages_of_user(chat: Chat,
                                     user: User,
                                     expected_messages: list[ChatMessage],
                                     ) -> None:
        assert chat.unread_messages_of_user(user.id) == expected_messages

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_user'), SetForTest.Chat.interlocutor_of_user)
    def test_interlocutor_of_user(chat: Chat,
                                  user: User,
                                  expected_user: User,
                                  ) -> None:
        assert chat.interlocutor_of_user(user.id) == expected_user

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user'), SetForTest.Chat.interlocutor_of_user_raises_value_error)
    def test_interlocutor_of_user_raises_value_error(chat: Chat,
                                                     user: User,
                                                     ) -> None:
        with pytest.raises(ValueError):
            chat.interlocutor_of_user(user.id)

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_unread_count'), SetForTest.Chat.unread_count_of_user)
    def test_unread_count_of_user(chat: Chat,
                                  user: User,
                                  expected_unread_count: int,
                                  ) -> None:
        assert chat.unread_count_of_user(user.id).value == expected_unread_count

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user'), SetForTest.Chat.unread_count_of_user_raises_permission_error)
    def test_unread_count_of_user_raises_permission_error(chat: Chat,
                                                          user: User,
                                                          ) -> None:
        with pytest.raises(PermissionError):
            chat.unread_count_of_user(user.id)


class TestChatMessage:

    @staticmethod
    @pytest.mark.parametrize(('storage_id', 'expected_message'), SetForTest.ChatMessage.by_storage_id)
    def test_by_storage_id(storage_id: int,
                           expected_message: ChatMessage,
                           ) -> None:
        assert ChatMessage.by_storage_id(storage_id) == expected_message


class TestUserChatMatch:

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user'), SetForTest.UserChatMatch.chat_if_user_has_access)
    def test_chat_if_user_has_access(chat: Chat,
                                     user: User,
                                     ) -> None:
        assert UserChatMatch.chat_if_user_has_access(user.id, chat.id) == chat

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user'), SetForTest.UserChatMatch.chat_if_user_has_access_raises_permission_error)
    def test_chat_if_user_has_access_raises_permission_error(chat: Chat,
                                                             user: User,
                                                             ) -> None:
        with pytest.raises(PermissionError):
            UserChatMatch.chat_if_user_has_access(user.id, chat.id)

    @staticmethod
    @pytest.mark.parametrize(('chat', 'expected_users'), SetForTest.UserChatMatch.users_of_chat)
    def test_users_of_chat(chat: Chat,
                           expected_users: list[User],
                           ) -> None:
        assert set(UserChatMatch.users_of_chat(chat.id)) == set(expected_users)

    @staticmethod
    @pytest.mark.parametrize(('user', 'expected_chats'), SetForTest.UserChatMatch.chats_of_user)
    def test_chats_of_user(user: User,
                           expected_chats: list[Chat],
                           ) -> None:
        assert UserChatMatch.chats_of_user(user.id) == expected_chats

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_user'), SetForTest.UserChatMatch.interlocutor_of_user_of_chat)
    def test_interlocutor_of_user_of_chat(chat: Chat,
                                          user: User,
                                          expected_user: User,
                                          ) -> None:
        assert UserChatMatch.interlocutor_of_user_of_chat(user.id, chat.id) == expected_user

    @staticmethod
    @pytest.mark.parametrize(('first_user', 'second_user', 'expected_chat'),
                             SetForTest.UserChatMatch.private_chat_between_users)
    def test_private_chat_between_users(first_user: User,
                                        second_user: User,
                                        expected_chat: Chat,
                                        ) -> None:
        assert UserChatMatch.private_chat_between_users(first_user.id, second_user.id) == expected_chat

    @staticmethod
    @pytest.mark.parametrize(('first_user', 'second_user'),
                             SetForTest.UserChatMatch.private_chat_between_users_raises_value_error)
    def test_private_chat_between_users_raises_value_error_if_chat_not_found(first_user: User,
                                                                             second_user: User,
                                                                             ) -> None:
        with pytest.raises(ValueError):
            UserChatMatch.private_chat_between_users(first_user.id, second_user.id)

    @staticmethod
    @pytest.mark.parametrize(('user', 'expected_users'), SetForTest.UserChatMatch.all_interlocutors_of_user)
    def test_all_interlocutors_of_user(user: User,
                                       expected_users: list[User],
                                       ) -> None:
        assert set(UserChatMatch.all_interlocutors_of_user(user.id)) == set(expected_users)

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_unread_count'),
                             SetForTest.UserChatMatch.unread_count_of_user_of_chat)
    def test_unread_count_of_user_of_chat(chat: Chat,
                                          user: User,
                                          expected_unread_count: int,
                                          ) -> None:
        assert UserChatMatch.unread_count_of_user_of_chat(user.id, chat.id).value == expected_unread_count

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user'),
                             SetForTest.UserChatMatch.unread_count_of_user_of_chat_raises_permission_error)
    def test_unread_count_of_user_of_chat_raises_permission_error(chat: Chat,
                                                                  user: User,
                                                                  ) -> None:
        with pytest.raises(PermissionError):
            UserChatMatch.unread_count_of_user_of_chat(user.id, chat.id)
