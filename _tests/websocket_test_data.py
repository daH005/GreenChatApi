from datetime import datetime

from api._tests.db_test_data import *  # noqa

COMMON_CREATING_DATETIME: datetime = datetime(
    year=2024, month=10, day=10,
)

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
                {'type': 'interlocutorsOnlineInfo',
                 'data': {
                     2: True,
                 }
                 }
            ],
            2: [
                {'type': 'interlocutorsOnlineInfo',
                 'data': {
                     1: True,
                 }
                 }
            ],
            4: [
                {'type': 'interlocutorsOnlineInfo',
                 'data': {
                     1: True,
                 }
                 }
            ],
            5: [
                {'type': 'interlocutorsOnlineInfo',
                 'data': {
                     1: True,
                 }
                 }
            ],
        }
    )
]

FULL_DISCONNECTION_HANDLER_SENDINGS = [
    (
        dict(
            user=USERS[1],
        ),
        {
            2: [
                {'type': 'interlocutorsOnlineInfo',
                 'data': {
                     1: False,
                 }
                 }
            ],
            4: [
                {'type': 'interlocutorsOnlineInfo',
                 'data': {
                     1: False,
                 }
                 }
            ],
            5: [
                {'type': 'interlocutorsOnlineInfo',
                 'data': {
                     1: False,
                 }
                 }
            ],
        }
    )
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
                {'type': 'interlocutorsOnlineInfo',
                 'data': {
                     3: True,
                 }
                 }
            ]
        }
    )
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
                         'creatingDatetime': COMMON_CREATING_DATETIME.isoformat(),
                         'user': {
                             'id': 1,
                             'firstName': USERS[1].first_name,
                             'lastName': USERS[1].last_name,
                         }
                     },
                     'users': [
                         {
                             'id': 1,
                             'firstName': USERS[1].first_name,
                             'lastName': USERS[1].last_name,
                         },
                         {
                             'id': 5,
                             'firstName': USERS[5].first_name,
                             'lastName': USERS[5].last_name,
                         },
                     ]
                 }
                 },
                {'type': 'interlocutorsOnlineInfo',
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
                         'creatingDatetime': COMMON_CREATING_DATETIME.isoformat(),
                         'user': {
                             'id': 1,
                             'firstName': USERS[1].first_name,
                             'lastName': USERS[1].last_name,
                         }
                     },
                     'users': [
                         {
                             'id': 1,
                             'firstName': USERS[1].first_name,
                             'lastName': USERS[1].last_name,
                         },
                         {
                             'id': 5,
                             'firstName': USERS[5].first_name,
                             'lastName': USERS[5].last_name,
                         },
                     ]
                 }
                 },
                {'type': 'interlocutorsOnlineInfo',
                 'data': {
                     1: True,
                 }
                 }
            ],
        }
    )
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
                     'creatingDatetime': COMMON_CREATING_DATETIME.isoformat(),
                     'user': {
                         'id': 1,
                         'firstName': USERS[1].first_name,
                         'lastName': USERS[1].last_name,
                     }
                 }
                 }
            ],
            2: [
                {'type': 'newChatMessage',
                 'data': {
                     'id': 6,
                     'chatId': 1,
                     'text': 'Hello...',
                     'creatingDatetime': COMMON_CREATING_DATETIME.isoformat(),
                     'user': {
                         'id': 1,
                         'firstName': USERS[1].first_name,
                         'lastName': USERS[1].last_name,
                     }
                 }
                 }
            ],
        }
    )
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
                     'user': {
                         'id': 1,
                         'firstName': USERS[1].first_name,
                         'lastName': USERS[1].last_name
                     }
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
                     'user': {
                         'id': 2,
                         'firstName': USERS[2].first_name,
                         'lastName': USERS[2].last_name
                     }
                 }
                 }
            ]
        }
    ),
]
