from api._tests.db_test_data import *  # noqa

FIRST_CONNECTION_HANDLER_SENT_DATA = [
    (
        dict(
            user=USERS[1],
        ),
        {
            1: [
                {'type': 'interlocutorsOnlineInfo',
                 'data': {}
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
