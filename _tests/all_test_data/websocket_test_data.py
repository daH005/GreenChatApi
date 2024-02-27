from api._tests.all_test_data.db_test_data import *  # noqa
from api._tests.common import COMMON_DATETIME  # noqa

ONLINE_USERS_IDS = [
    1, 2, 3, 5
]

USERS_IDS_AND_POTENTIAL_INTERLOCUTORS_IDS = {
    1: [
        5,
    ],
}

FIRST_CONNECTION_HANDLER_SENDINGS = [
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

FULL_DISCONNECTION_HANDLER_SENDINGS = [
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

ONLINE_STATUS_TRACING_ADDING_HANDLER_SENDINGS = [
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

NEW_CHAT_HANDLER_SENDINGS = [
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

NEW_CHAT_MESSAGE_HANDLER_SENDINGS = [
    (
        dict(
            user=USERS[1],
            data={
                'chatId': 1,
                'text': 'Hello...',
            }
        ),
        {
            1: [
                {'type': 'newChatMessage',
                 'data': {
                     'id': 6,
                     'chatId': 1,
                     'text': 'Hello...',
                     'creatingDatetime': COMMON_DATETIME.isoformat(),
                     'userId': 1,
                     'isRead': False,
                 }
                 }
            ],
            2: [
                {'type': 'newChatMessage',
                 'data': {
                     'id': 6,
                     'chatId': 1,
                     'text': 'Hello...',
                     'creatingDatetime': COMMON_DATETIME.isoformat(),
                     'userId': 1,
                     'isRead': False,
                 }
                 }
            ],
        }
    ),
]

NEW_CHAT_MESSAGE_TYPING_HANDLER_SENDINGS = [
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

CHAT_MESSAGE_WAS_READ_HANDLER_SENDINGS = [
    (
        dict(
            user=USERS[2],
            data={
                'chatMessageId': 1,
            }
        ),
        {
            1: [
                {'type': 'chatMessageWasRead',
                 'data': {
                    'chatId': 1,
                    'chatMessageId': 1,
                 }
                 },
            ]
        }
    ),
    (
        dict(
            user=USERS[1],
            data={
                'chatMessageId': 2,
            }
        ),
        {
            2: [
                {'type': 'chatMessageWasRead',
                 'data': {
                    'chatId': 1,
                    'chatMessageId': 2,
                 }
                 },
            ]
        }
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
