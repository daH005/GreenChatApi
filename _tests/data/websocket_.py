from api._tests.data.db import *
from api._tests.common import COMMON_DATETIME

ONLINE_USERS_IDS = [
    1, 2, 3, 5
]

USERS_IDS_AND_POTENTIAL_INTERLOCUTORS_IDS = {
    1: [
        5,
    ],
}

EACH_CONNECTION_HANDLER_KWARGS_AND_SERVER_MESSAGES = [
    (
        dict(
            user=USERS[1],
        ),
        {
            1: [
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     2: True,
                 }
                 }
            ],
            2: [
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     1: True,
                 }
                 }
            ],
            4: [
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     1: True,
                 }
                 }
            ],
            5: [
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     1: True,
                 }
                 }
            ],
        }
    ),
]

FULL_DISCONNECTION_HANDLER_KWARGS_AND_SERVER_MESSAGES = [
    (
        dict(
            user=USERS[1],
        ),
        {
            2: [
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     1: False,
                 }
                 }
            ],
            4: [
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     1: False,
                 }
                 }
            ],
            5: [
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     1: False,
                 }
                 }
            ],
        }
    ),
]

ONLINE_STATUS_TRACING_ADDING_HANDLER_KWARGS_AND_SERVER_MESSAGES = [
    (
        dict(
            user=USERS[1],
            data={
                'userId': 3,
            }
        ),
        {
            1: [
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     3: True,
                 }
                 }
            ]
        }
    ),
]

NEW_CHAT_HANDLER_KWARGS_AND_SERVER_MESSAGES = [
    (
        dict(
            user=USERS[1],
            data={
                'usersIds': [1, 5],
                'text': 'Hi!',
            }
        ),
        {
            1: [
                {'type': 'newChat',
                 'data': {
                     'id': 5,
                     'name': None,
                     'isGroup': False,
                     'unreadCount': 0,
                     'lastMessage': {
                         'id': 5,
                         'chatId': 5,
                         'text': 'Hi!',
                         'creatingDatetime': COMMON_DATETIME.isoformat(),
                         'userId': 1,
                         'isRead': False,
                     },
                     'usersIds': [1, 5]
                 }
                 },
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     5: True,
                 }
                 }
            ],
            5: [
                {'type': 'newChat',
                 'data': {
                     'id': 5,
                     'name': None,
                     'isGroup': False,
                     'unreadCount': 1,
                     'lastMessage': {
                         'id': 5,
                         'chatId': 5,
                         'text': 'Hi!',
                         'creatingDatetime': COMMON_DATETIME.isoformat(),
                         'userId': 1,
                         'isRead': False,
                     },
                     'usersIds': [1, 5]
                 }
                 },
                {'type': 'interlocutorsOnlineStatuses',
                 'data': {
                     1: True,
                 }
                 }
            ],
        }
    ),
]

NEW_CHAT_HANDLER_KWARGS_AND_EXCEPTIONS = [
    (
        dict(
            user=USERS[1],
            data={
                'text': 'Hi!',
                'usersIds': [2],
                'name': None,
                'isGroup': False,
            }
        ),
        ValueError
    ),
    (
        dict(
            user=USERS[1],
            data={
                'text': 'Hi!',
                'usersIds': [1, 5, 7],
                'name': None,
                'isGroup': False,
            }
        ),
        ValueError
    ),
    (
        dict(
            user=USERS[1],
            data={
                'text': 'Hi!',
                'usersIds': [1, 5],
                'name': None,
                'isGroup': False,
            }
        ),
        ValueError
    ),
]

NEW_CHAT_MESSAGE_HANDLER_KWARGS_AND_SERVER_MESSAGES = [
    (
        dict(
            user=USERS[1],
            data={
                'chatId': 5,
                'text': 'Hello...',
            }
        ),
        {
            1: [
                {'type': 'newChatMessage',
                 'data': {
                     'id': 6,
                     'chatId': 5,
                     'text': 'Hello...',
                     'creatingDatetime': COMMON_DATETIME.isoformat(),
                     'userId': 1,
                     'isRead': False,
                 }
                 }
            ],
            5: [
                {'type': 'newUnreadCount',
                 'data': {
                     'chatId': 5,
                     'unreadCount': 2,
                 }
                 },
                {'type': 'newChatMessage',
                 'data': {
                     'id': 6,
                     'chatId': 5,
                     'text': 'Hello...',
                     'creatingDatetime': COMMON_DATETIME.isoformat(),
                     'userId': 1,
                     'isRead': False,
                 }
                 },
            ],
        }
    ),
    (
        dict(
            user=USERS[1],
            data={
                'chatId': 5,
                'text': 'Hello 2...',
            }
        ),
        {
            1: [
                {'type': 'newChatMessage',
                 'data': {
                     'id': 7,
                     'chatId': 5,
                     'text': 'Hello 2...',
                     'creatingDatetime': COMMON_DATETIME.isoformat(),
                     'userId': 1,
                     'isRead': False,
                 }
                 }
            ],
            5: [
                {'type': 'newUnreadCount',
                 'data': {
                     'chatId': 5,
                     'unreadCount': 3,
                 }
                 },
                {'type': 'newChatMessage',
                 'data': {
                     'id': 7,
                     'chatId': 5,
                     'text': 'Hello 2...',
                     'creatingDatetime': COMMON_DATETIME.isoformat(),
                     'userId': 1,
                     'isRead': False,
                 }
                 },
            ],
        }
    ),
]

NEW_CHAT_MESSAGE_HANDLER_KWARGS_AND_EXCEPTIONS = [
    (
        dict(
            user=USERS[2],
            data={
                'chatId': 5,
                'text': 'Hi!',
            }
        ),
        PermissionError
    ),
]

NEW_CHAT_MESSAGE_TYPING_HANDLER_KWARGS_AND_SERVER_MESSAGES = [
    (
        dict(
            user=USERS[1],
            data={
                'chatId': 1,
            }
        ),
        {
            2: [
                {'type': 'newChatMessageTyping',
                 'data': {
                     'chatId': 1,
                     'userId': 1
                 }
                 }
            ]
        }
    ),
    (
        dict(
            user=USERS[2],
            data={
                'chatId': 1,
            }
        ),
        {
            1: [
                {'type': 'newChatMessageTyping',
                 'data': {
                     'chatId': 1,
                     'userId': 2
                 }
                 }
            ]
        }
    ),
]

NEW_CHAT_MESSAGE_TYPING_HANDLER_KWARGS_AND_EXCEPTIONS = [
    (
        dict(
            user=USERS[2],
            data={
                'chatId': 5,
            }
        ),
        PermissionError
    ),
]

CHAT_MESSAGE_WAS_READ_HANDLER_KWARGS_AND_SERVER_MESSAGES = [
    (
        dict(
            user=USERS[5],
            data={
                'chatId': 5,
                'chatMessageId': 1,
            }
        ),
        {}
    ),
    (
        dict(
            user=USERS[5],
            data={
                'chatId': 5,
                'chatMessageId': 5,
            }
        ),
        {
            1: [
                {'type': 'readChatMessages',
                 'data': {
                     'chatId': 5,
                     'chatMessagesIds': [5],
                 }
                 },
            ],
            5: [
                {'type': 'newUnreadCount',
                 'data': {
                     'chatId': 5,
                     'unreadCount': 2,
                 }
                 }
            ]
        }
    ),
    (
        dict(
            user=USERS[5],
            data={
                'chatId': 5,
                'chatMessageId': 7,
            }
        ),
        {
            1: [
                {'type': 'readChatMessages',
                 'data': {
                     'chatId': 5,
                     'chatMessagesIds': [6, 7],
                 }
                 },
            ],
            5: [
                {'type': 'newUnreadCount',
                 'data': {
                     'chatId': 5,
                     'unreadCount': 0,
                 }
                 }
            ]
        }
    ),
]

CHAT_MESSAGE_WAS_READ_HANDLER_KWARGS_AND_EXCEPTIONS = [
    (
        dict(
            user=USERS[2],
            data={
                'chatId': 5,
                'chatMessageId': 5,
            }
        ),
        PermissionError
    ),
]

RAW_AND_HANDLED_MESSAGES_TEXTS = [
    (
        'Hi! 1 2 3\n1 2 3',
        'Hi! 1 2 3\n1 2 3',
    ),
    (
        '   Hello!   How are u??\n  \n\n   My name is Danil!  \n',
        'Hello! How are u??\nMy name is Danil!',
    ),
]
