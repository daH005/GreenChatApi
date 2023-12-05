import pytest
from datetime import datetime

from api.json_ import *
from api.db.models import *
from common import make_random_string


def _make_test_chat_message(user: User, **kwargs) -> ChatMessage:
    """Создаёт объект `ChatMessage` с модификациями под тестовые нужды."""
    chat_message = ChatMessage(**kwargs)
    chat_message.user = user
    chat_message.creating_datetime = datetime.utcnow()
    return chat_message


def _make_test_chat(messages: list[ChatMessage],
                    interlocutor_name: str | None = None,
                    **kwargs) -> Chat:
    """Создаёт объект `Chat` с модификациями под тестовые нужды."""
    chat = Chat(**kwargs)
    chat.interlocutor_name = interlocutor_name
    # `Chat.messages` является `property`, поэтому используем следующую технику.
    chat.__dict__['messages'] = messages
    return chat


# Тестовые пользователи.
USERS = [
    User(
        id=1,
        username='user1',
        auth_token='pass',
        email='dan@mail.ru',
        first_name='first_name228',
        last_name='last_name',
    ),
    User(
        id=2,
        username='user2',
        auth_token='----supertoken----',  # noqa
        email='dan123@mail.ru',
        first_name='first_name1',
        last_name='last_name',
    ),
    User(
        id=3,
        username='dan005',
        auth_token='try-hack-man!',
        email='dan228@mail.ru',
        first_name='first_name',
        last_name='last_name2',
    ),
]
# Тестовые сообщения.
CHATS_MESSAGES = [
    _make_test_chat_message(
        user=USERS[1],
        id=1,
        user_id=2,
        chat_id=3,
        text='Hello...'
    ),
    _make_test_chat_message(
        user=USERS[2],
        id=2,
        user_id=3,
        chat_id=2,
        text='By!'
    ),
    _make_test_chat_message(
        user=USERS[0],
        id=3,
        user_id=1,
        chat_id=2,
        text='What?!'
    ),
    _make_test_chat_message(
        user=USERS[0],
        id=4,
        user_id=1,
        chat_id=3,
        text='Sorry... My bad.'
    ),
    _make_test_chat_message(
        user=USERS[1],
        id=5,
        user_id=2,
        chat_id=1,
        text='Sorry... My bad.'
    ),
]
# Тестовые чаты.
CHATS = [
    _make_test_chat(
        messages=CHATS_MESSAGES[:1],
        id=1,
        name='Беседка',
    ),
    _make_test_chat(
        messages=CHATS_MESSAGES[2:3],
        id=2,
        interlocutor_name='user100',
        name=None,
    ),
    _make_test_chat(
        messages=CHATS_MESSAGES,
        id=3,
        interlocutor_name='dan005',
        name=None,
    ),
]


@pytest.mark.parametrize('auth_token', [
    make_random_string() for _ in range(5)
])
def test_auth_token_to_json_dict(auth_token: str) -> None:
    """Позитивный тест: формирование словаря с токеном."""
    assert JSONDictPreparer.prepare_jwt_token(auth_token) == {
        'JWTToken': auth_token,
    }


@pytest.mark.parametrize(('user', 'exclude_important_info'), zip(USERS, [True, True, False]))
def test_user_info_to_json_dict(user: User,
                                exclude_important_info: bool,
                                ) -> None:
    """Позитивный тест: формирование словаря с информацией о пользователе."""
    expected_dict = {
        'id': user.id,
        'username': user.username,
        'firstName': user.first_name,
        'lastName': user.last_name,
    }
    if not exclude_important_info:
        expected_dict['email'] = user.email
    assert JSONDictPreparer.prepare_user_info(user, exclude_important_info) == expected_dict


@pytest.mark.parametrize('chat', CHATS)
def test_chat_history_to_json_dict(chat: Chat) -> None:
    """Позитивный тест: формирование словаря с историей чата."""
    expected_dict = {
        'messages': []
    }
    for chat_message in chat.messages:
        expected_dict['messages'].append({
            'id': chat_message.id,
            'user': {
                'id': chat_message.user.id,
                'username': chat_message.user.username,
                'firstName': chat_message.user.first_name,
                'lastName': chat_message.user.last_name,
            },
            'chatId': chat_message.chat_id,
            'text': chat_message.text,
            'creatingDatetime': chat_message.creating_datetime.isoformat(),
        })
    assert JSONDictPreparer.prepare_chat_history(chat.messages) == expected_dict


@pytest.mark.parametrize('chat_message', CHATS_MESSAGES)
def test_chat_message_to_json_dict(chat_message: ChatMessage) -> None:
    """Позитивный тест: формирование словаря сообщения."""
    assert JSONDictPreparer.prepare_chat_message(chat_message) == {
        'id': chat_message.id,
        'user': {
            'id': chat_message.user.id,
            'username': chat_message.user.username,
            'firstName': chat_message.user.first_name,
            'lastName': chat_message.user.last_name,
        },
        'chatId': chat_message.chat_id,
        'text': chat_message.text,
        'creatingDatetime': chat_message.creating_datetime.isoformat(),
    }


@pytest.mark.parametrize(('user_chats', 'user_id'), [
    (CHATS, 1),
    (CHATS[1:], 3),
    (CHATS[:2], 2),
])
def test_user_chats_to_json_dict(user_chats: list[Chat],
                                 user_id: int,
                                 ) -> None:
    """Позитивный тест: формирование словаря с чатами, в которых состоит пользователь."""
    expected_dict = {
        'chats': []
    }
    for chat in user_chats:
        expected_dict['chats'].append({
            'id': chat.id,
            'name': chat.name,
            'interlocutor': chat.interlocutor(user_id),
            'lastMessage': {
                'id': chat.last_message.id,
                'user': {
                    'id': chat.last_message.user.id,
                    'username': chat.last_message.user.username,
                    'firstName': chat.last_message.user.first_name,
                    'lastName': chat.last_message.user.last_name,
                },
                'chatId': chat.last_message.chat_id,
                'text': chat.last_message.text,
                'creatingDatetime': chat.last_message.creating_datetime.isoformat(),
            },
        })
    assert JSONDictPreparer.prepare_user_chats(user_chats, user_id) == expected_dict
