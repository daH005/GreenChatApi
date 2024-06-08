from api.db.models import *
from api._tests.common import make_random_string  # noqa

USERS = {
    1: User(
        email='dan@mail.ru',
        first_name='first_name',
        last_name='last_name',
    ),
    2: User(
        email='dan123@mail.ru',
        first_name='first_name',
        last_name='last_name',
    ),
    3: User(
        email='dan228@mail.ru',
        first_name='first_name',
        last_name='last_name',
    ),
    4: User(
        email='dan22811@mail.ru',
        first_name='first_name',
        last_name='last_name',
    ),
    5: User(
        email='pochta@yandex.ru',
        first_name='danil',
        last_name='shevelev',  # noqa
    )
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

UNREAD_COUNTS = [
    UnreadCount(
        user_chat_match_id=1,
    ),
    UnreadCount(
        user_chat_match_id=2,
    ),
    UnreadCount(
        user_chat_match_id=3,
    ),
    UnreadCount(
        user_chat_match_id=4,
    ),
    UnreadCount(
        user_chat_match_id=5,
    ),
    UnreadCount(
        user_chat_match_id=6,
    ),
    UnreadCount(
        user_chat_match_id=7,
    ),
]

CHATS_INTERLOCUTORS = [
    (CHATS[1], USERS[1], USERS[2]),
    (CHATS[2], USERS[4], USERS[1]),
]

USERS_CHATS = [
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

USERS_IN_CHATS = [
    (CHATS[1], [USERS[1], USERS[2]]),
    (CHATS[2], [USERS[1], USERS[4]]),
    (CHATS[3], [USERS[1], USERS[2], USERS[4]]),
    (CHATS[4], [])
]

CHATS_ACCESS_FOR_USERS = [
    (USERS[1], CHATS[1]),
    (USERS[1], CHATS[2]),
    (USERS[1], CHATS[3]),
    (USERS[2], CHATS[1]),
    (USERS[4], CHATS[2]),
]

CHATS_NO_ACCESS_FOR_USERS = [
    (USERS[1], CHATS[4]),
    (USERS[2], CHATS[4]),
    (USERS[2], CHATS[2]),
    (USERS[3], CHATS[1]),
    (USERS[3], CHATS[2]),
    (USERS[3], CHATS[3]),
    (USERS[3], CHATS[4]),
]

PRIVATE_CHATS_USERS = [
    (USERS[1], USERS[2], CHATS[1]),
    (USERS[1], USERS[4], CHATS[2]),
]

USERS_WITHOUT_PRIVATE_CHAT = [
    (USERS[1], USERS[3]),
    (USERS[2], USERS[3]),
    (USERS[2], USERS[4]),
]

ALL_INTERLOCUTORS_OF_USERS = [
    (USERS[1], [
        USERS[2],
        USERS[4],
    ]),
    (USERS[2], [
        USERS[1],
        USERS[4],
    ]),
    (USERS[4], [
        USERS[1],
        USERS[2],
    ]),
    (USERS[3], []),
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


def prepare_test_db() -> None:
    DBBuilder.init_session('sqlite:///:memory:')

    BaseModel.metadata.create_all(bind=DBBuilder.engine)
    DBBuilder.session.add_all([
        *USERS.values(),
        *CHATS.values(),
        *USERS_CHATS_MATCHES,
        *UNREAD_COUNTS,
    ])
    DBBuilder.session.commit()

    # for exact `creating_datetime`:
    for message in CHATS_MESSAGES:
        DBBuilder.session.add(message)
        DBBuilder.session.commit()


prepare_test_db()
