from api._tests.all_test_data.db_test_data import *  # noqa
from api._tests.common import COMMON_DATETIME  # noqa

JWT_TOKEN_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            jwt_token='TOKEN',
        ),
        {
            'JWTToken': 'TOKEN',
        }
    )
]

ALREADY_TAKEN_FLAG_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            flag=False,
        ),
        {
            'isAlreadyTaken': False,
        }
    ),
    (
        dict(
            flag=True,
        ),
        {
            'isAlreadyTaken': True,
        }
    ),
]

CODE_IS_VALID_FLAG_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            flag=False,
        ),
        {
            'codeIsValid': False,
        }
    ),
    (
        dict(
            flag=True,
        ),
        {
            'codeIsValid': True,
        }
    ),
]

USER_CHATS_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            user_chats=USERS_CHATS[0][1],
        ),
        {
            'chats': [
                {
                    'id': 3,
                    'isGroup': True,
                    'name': 'Беседа',
                    'usersIds': [1, 2, 4],
                    'lastMessage': {
                        'id': 4,
                        'chatId': 3,
                        'creatingDatetime': COMMON_DATETIME.isoformat(),
                        'userId': 1,
                        'text': 'And?..',
                        'isRead': False,
                    }
                },
                {
                    'id': 2,
                    'isGroup': False,
                    'name': None,
                    'usersIds': [1, 4],
                    'lastMessage': {
                        'id': 3,
                        'chatId': 2,
                        'creatingDatetime': COMMON_DATETIME.isoformat(),
                        'userId': 1,
                        'text': 'Yup.',
                        'isRead': False,
                    }
                },
                {
                    'id': 1,
                    'isGroup': False,
                    'name': None,
                    'usersIds': [1, 2],
                    'lastMessage': {
                        'id': 2,
                        'chatId': 1,
                        'creatingDatetime': COMMON_DATETIME.isoformat(),
                        'userId': 2,
                        'text': 'Hello! How are u?',
                        'isRead': False,
                    }
                },
            ]
        }
    ),
]

CHAT_INFO_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            chat=CHATS[1],
        ),
        {
            'id': 1,
            'isGroup': False,
            'name': None,
            'usersIds': [1, 2],
            'lastMessage': {
                'id': 2,
                'chatId': 1,
                'creatingDatetime': COMMON_DATETIME.isoformat(),
                'userId': 2,
                'text': 'Hello! How are u?',
                'isRead': False,
            }
        },
    ),
]

USER_INFO_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            user=USERS[1],
            exclude_important_info=True,
        ),
        {
            'id': 1,
            'firstName': 'first_name',
            'lastName': 'last_name',
        }
    ),
    (
        dict(
            user=USERS[1],
            exclude_important_info=False,
        ),
        {
            'id': 1,
            'firstName': 'first_name',
            'lastName': 'last_name',
            'email': 'dan@mail.ru',
            'username': 'user1',
        }
    ),
]

CHAT_HISTORY_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            chat_messages=CHATS[1].messages,
        ),
        {
            'messages': [
                {
                    'id': 2,
                    'chatId': 1,
                    'creatingDatetime': COMMON_DATETIME.isoformat(),
                    'userId': 2,
                    'text': 'Hello! How are u?',
                    'isRead': False,
                },
                {
                    'id': 1,
                    'chatId': 1,
                    'creatingDatetime': COMMON_DATETIME.isoformat(),
                    'userId': 1,
                    'text': 'Hi!',
                    'isRead': False,
                },
            ]
        }
    ),
]

CHAT_MESSAGE_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            chat_message=CHATS_MESSAGES[1],
        ),
        {
            'id': 2,
            'chatId': 1,
            'creatingDatetime': COMMON_DATETIME.isoformat(),
            'userId': 2,
            'text': 'Hello! How are u?',
            'isRead': False,
        },
    ),
]

CHAT_MESSAGE_TYPING_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            user_id=1,
            chat_id=2,
        ),
        {
            'userId': 1,
            'chatId': 2,
        }
    ),
]
