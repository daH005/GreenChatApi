from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import create_session, Session

from api.db import models
from api.db.models import *
from api._tests.common import make_random_string  # noqa

USERS_PASSWORDS = {
    1: 'test_pass123',
    2: 'test_pass__',
    3: 'test_pass__',
    4: 'test_pass__44',
    5: 'new...213123'
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
    5: User.new_by_password(
        'dan',
        USERS_PASSWORDS[5],
        'pochta@yandex.ru',
        'danil',
        'shevelev',  # noqa
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

ALREADY_TAKEN_AND_NOT_USERNAMES = [
    ('hi!111111111', False),
    (USERS[1].username, True),
    (USERS[2].username, True),
    (USERS[3].username, True),
    (USERS[4].username, True),
    ('new11', False),
]

ALREADY_TAKEN_AND_NOT_EMAILS = [
    ('hi!111111111@mail.ru', False),
    (USERS[1].email, True),
    (USERS[2].email, True),
    (USERS[3].email, True),
    (USERS[4].email, True),
    ('new11@yandex.ru', False),
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


# DB FULLING!
_prepare_test_db()
