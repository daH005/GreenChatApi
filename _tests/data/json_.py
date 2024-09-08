from _tests.data.db import (
    USERS_CHATS,
    CHATS,
    USERS,
    CHATS_MESSAGES,
)
from _tests.common_ import COMMON_DATETIME

__all__ = (
    'CODE_IS_VALID_FLAG_KWARGS_AND_JSON_DICTS',
    'USER_CHATS_KWARGS_AND_JSON_DICTS',
    'CHAT_INFO_KWARGS_AND_JSON_DICTS',
    'USER_INFO_KWARGS_AND_JSON_DICTS',
    'CHAT_HISTORY_KWARGS_AND_JSON_DICTS',
    'CHAT_MESSAGE_KWARGS_AND_JSON_DICTS',
    'NEW_UNREAD_COUNT_KWARGS_AND_JSON_DICTS',
    'READ_CHAT_MESSAGES_KWARGS_AND_JSON_DICTS',
    'CHAT_MESSAGE_TYPING_KWARGS_AND_JSON_DICTS',
)

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
            user_id=1,
        ),
        {
            'chats': [
                {
                    'id': 3,
                    'isGroup': True,
                    'name': 'Беседа',
                    'usersIds': [1, 2, 4],
                    'unreadCount': 0,
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
                    'unreadCount': 0,
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
                    'unreadCount': 0,
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
            user_id=1,
        ),
        {
            'id': 1,
            'isGroup': False,
            'name': None,
            'usersIds': [1, 2],
            'unreadCount': 0,
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

NEW_UNREAD_COUNT_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            chat_id=1,
            unread_count=5,
        ),
        {
            'chatId': 1,
            'unreadCount': 5,
        }
    ),
]

READ_CHAT_MESSAGES_KWARGS_AND_JSON_DICTS = [
    (
        dict(
            chat_id=1,
            chat_messages_ids=[1, 2, 3],
        ),
        {
            'chatId': 1,
            'chatMessagesIds': [1, 2, 3],
        }
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
