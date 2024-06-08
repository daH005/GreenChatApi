import pytest
from datetime import datetime, timedelta

from api._tests.all_test_data.db_test_data import *  # noqa: must be first!
from api.db.models import *  # noqa


class AbstractTestModel:
    Model: type[User] | type[Chat] | type[ChatMessage] | type[UserChatMatch] | type[UnreadCount]
    ATTRS_NAMES: tuple[str]

    @classmethod
    def test_positive_model_has_required_attrs(cls) -> None:
        for attr_name in cls.ATTRS_NAMES:
            assert hasattr(cls.Model, attr_name)


class TestUser(AbstractTestModel):
    Model = User
    ATTRS_NAMES = (
        'id',
        'email',
        'first_name',
        'last_name',
    )


class TestChat(AbstractTestModel):
    Model = Chat
    ATTRS_NAMES = (
        'id',
        'name',
        'is_group',
        'messages',
    )

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


class TestChatMessage(AbstractTestModel):
    Model = ChatMessage
    ATTRS_NAMES = (
        'id',
        'user_id',
        'chat_id',
        'text',
        'creating_datetime',
        'is_read',
        'user',
        'chat',
    )

    @staticmethod
    @pytest.mark.parametrize('text', TEXT_MESSAGES)
    def test_positive_creating_datetime_is_current_datetime(text: str) -> None:
        chat_message = ChatMessage(
            user_id=1,
            chat_id=1,
            text=text,
        )
        DBBuilder.session.add(chat_message)
        DBBuilder.session.flush()
        max_datetime = datetime.utcnow() + timedelta(milliseconds=10)
        min_datetime = datetime.utcnow() - timedelta(milliseconds=10)
        assert max_datetime >= chat_message.creating_datetime >= min_datetime
        DBBuilder.session.rollback()


class TestUserChatMatch(AbstractTestModel):
    Model = UserChatMatch
    ATTRS_NAMES = (
        'id',
        'user_id',
        'chat_id',
        'user',
        'chat',
        'unread_count',
    )

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


class TestUnreadCount(AbstractTestModel):
    Model = UnreadCount
    ATTRS_NAMES = (
        'id',
        'user_chat_match_id',
        'value',
        'user_chat_match',
    )
