import pytest

from db.models import (
    User,
    Chat,
    ChatMessage,
    UserChatMatch,
    UnreadCount,
)
from _tests.data.db import (
    CHATS_INTERLOCUTORS,
    USERS_CHATS,
    CHATS_USERS,
    USERS_AND_CHATS_AVAILABLE_FOR_THEM,
    USERS_AND_CHATS_NOT_AVAILABLE_FOR_THEM,
    USERS_PAIRS_AND_THEIR_PRIVATE_CHATS,
    USERS_PAIRS_WITHOUT_PRIVATE_CHAT,
    USERS_ALL_INTERLOCUTORS,
)


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


class TestChatMessage(AbstractTestModel):
    Model = ChatMessage
    ATTRS_NAMES = (
        'id',
        'user_id',
        'chat_id',
        'text',
        'creating_datetime',
        'is_read',
        'has_files',
        'user',
        'chat',
    )


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
    @pytest.mark.parametrize(('user', 'chat'), USERS_AND_CHATS_AVAILABLE_FOR_THEM)
    def test_positive_chat_if_user_has_access(user: User,
                                              chat: Chat,
                                              ) -> None:
        assert UserChatMatch.chat_if_user_has_access(user.id, chat.id) == chat

    @staticmethod
    @pytest.mark.parametrize(('user', 'chat'), USERS_AND_CHATS_NOT_AVAILABLE_FOR_THEM)
    def test_negative_chat_if_user_has_access_raises_permission_error_if_user_has_not_access_to_chat(user: User,
                                                                                                     chat: Chat,
                                                                                                     ) -> None:
        with pytest.raises(PermissionError):
            UserChatMatch.chat_if_user_has_access(user.id, chat.id)

    @staticmethod
    @pytest.mark.parametrize(('chat', 'expected_users'), CHATS_USERS)
    def test_positive_users_of_chat(chat: Chat,
                                    expected_users: list[User],
                                    ) -> None:
        assert set(UserChatMatch.users_of_chat(chat.id)) == set(expected_users)

    @staticmethod
    @pytest.mark.parametrize(('user', 'expected_chats'), USERS_CHATS)
    def test_positive_chats_of_user(user: User,
                                    expected_chats: list[Chat],
                                    ) -> None:
        assert UserChatMatch.chats_of_user(user.id) == expected_chats

    @staticmethod
    @pytest.mark.parametrize(('chat', 'user', 'expected_user'), CHATS_INTERLOCUTORS)
    def test_positive_interlocutor_of_user_of_chat(chat: Chat,
                                                   user: User,
                                                   expected_user: User,
                                                   ) -> None:
        assert UserChatMatch.interlocutor_of_user_of_chat(user.id, chat.id) == expected_user

    @staticmethod
    @pytest.mark.parametrize(('first_user', 'second_user', 'expected_chat'), USERS_PAIRS_AND_THEIR_PRIVATE_CHATS)
    def test_positive_private_chat_between_users(first_user: User,
                                                 second_user: User,
                                                 expected_chat: Chat,
                                                 ) -> None:
        assert UserChatMatch.private_chat_between_users(first_user.id, second_user.id) == expected_chat

    @staticmethod
    @pytest.mark.parametrize(('first_user', 'second_user'), USERS_PAIRS_WITHOUT_PRIVATE_CHAT)
    def test_negative_private_chat_between_users_raises_value_error_if_chat_not_found(first_user: User,
                                                                                      second_user: User,
                                                                                      ) -> None:
        with pytest.raises(ValueError):
            UserChatMatch.private_chat_between_users(first_user.id, second_user.id)

    @staticmethod
    @pytest.mark.parametrize(('user', 'expected_users'), USERS_ALL_INTERLOCUTORS)
    def test_positive_all_interlocutors_of_user(user: User,
                                                expected_users: list[User],
                                                ) -> None:
        assert set(UserChatMatch.all_interlocutors_of_user(user.id)) == set(expected_users)


class TestUnreadCount(AbstractTestModel):
    Model = UnreadCount
    ATTRS_NAMES = (
        'id',
        'user_chat_match_id',
        'value',
        'user_chat_match',
    )
