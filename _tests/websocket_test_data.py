from api._tests.db_test_data import *  # noqa

ONLINE_USERS_IDS = [
    1, 2, 3,
]

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

]

NEW_CHAT_MESSAGE_HANDLER_SENDINGS = [

]

NEW_CHAT_MESSAGE_TYPING_HANDLER_SENDINGS = [

]
