import pytest

from api.db.models import *


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
    """Тест: модель пользователя должна иметь необходимый перечень атрибутов."""
    assert hasattr(User, attr_name)


@pytest.mark.parametrize('attr_name', [
    'id',
    'name',
    'messages',
    'last_message',
])
def test_chat_has_required_attrs(attr_name: str) -> None:
    """Тест: модель чата должна иметь необходимый перечень атрибутов."""
    assert hasattr(Chat, attr_name)


@pytest.mark.parametrize('attr_name', [
    'id',
    'user_id',
    'chat_id',
    'user',
    'text',
    'creating_datetime',
])
def test_chat_message_has_required_attrs(attr_name: str) -> None:
    """Тест: модель сообщения должна иметь необходимый перечень атрибутов."""
    assert hasattr(ChatMessage, attr_name)


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
    """Тест: модель доступа к чату должна иметь необходимый перечень атрибутов."""
    assert hasattr(UserChatMatch, attr_name)
