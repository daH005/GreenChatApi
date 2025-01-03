from db.models import User
from _tests.common.anything_place import anything

__all__ = (
    'ORMObjects',
    'Params',
    'SetForTest',
)


class ORMObjects:

    users = [
        User(
            _email='user1@mail.ru',
        ),
        User(
            _email='user2@mail.ru',
        ),
        User(
            _email='user3@mail.ru',
        ),
    ]


class Params:

    online_user_ids = [
        1, 2,
    ]

    user_ids_and_potential_interlocutor_ids = {
        3: [
            1,
        ],
    }


class SetForTest:

    online_status_tracing_adding_input_and_output = [
        (
            (
                ORMObjects.users[2],
                {
                    'type': 'onlineStatusTracingAdding',
                    'data': {
                        'userId': 1,
                    },
                },
            ),
            {
                3: [
                    {
                        'type': 'interlocutorsOnlineStatuses',
                        'data': {
                            1: True,
                        },
                    },
                ],
            },
        ),
        (
            (
                ORMObjects.users[1],
                {
                    'type': 'onlineStatusTracingAdding',
                    'data': {
                        'userId': 3,
                    },
                },
            ),
            {
                2: [
                    {
                        'type': 'interlocutorsOnlineStatuses',
                        'data': {
                            3: False,
                        },
                    },
                ],
            },
        ),
    ]

    new_chat_input_and_output = [
        (
            (
                ORMObjects.users[0],
                {
                    'type': 'newChat',
                    'data': {
                        'usersIds': [2],
                    },
                },
            ),
            {
                1: [
                    {
                        'type': 'newChat',
                        'data': {
                            'id': 1,
                            'isGroup': False,
                            'lastMessage': None,
                            'name': None,
                            'unreadCount': 0,
                            'usersIds': [2, 1],
                        },
                    },
                    {
                        'type': 'interlocutorsOnlineStatuses',
                        'data': {
                            2: True,
                        },
                    },
                ],
                2: [
                    {
                        'type': 'newChat',
                        'data': {
                            'id': 1,
                            'isGroup': False,
                            'lastMessage': None,
                            'name': None,
                            'unreadCount': 0,
                            'usersIds': [2, 1],
                        },
                    },
                    {
                        'type': 'interlocutorsOnlineStatuses',
                        'data': {
                            1: True,
                        },
                    },
                ],
            },
        ),
    ]

    new_chat_message_input_and_output = [
        (
            (
                ORMObjects.users[0],
                {
                    'type': 'newChatMessage',
                    'data': {
                        'chatId': 1,
                        'text': 'Hello!',
                    },
                },
            ),
            {
                2: [
                    {
                        'type': 'newUnreadCount',
                        'data': {
                            'chatId': 1,
                            'unreadCount': 1,
                        },
                    },
                    {
                        'type': 'newChatMessage',
                        'data': {
                            'id': 1,
                            'chatId': 1,
                            'userId': 1,
                            'text': 'Hello!',
                            'isRead': False,
                            'storageId': None,
                            'creatingDatetime': anything,
                        },
                    },
                ],
                1: [
                    {
                        'type': 'newChatMessage',
                        'data': {
                            'id': 1,
                            'chatId': 1,
                            'userId': 1,
                            'text': 'Hello!',
                            'isRead': False,
                            'storageId': None,
                            'creatingDatetime': anything,
                        },
                    },
                ],
            },
        ),

        (
            (
                ORMObjects.users[0],
                {
                    'type': 'newChatMessage',
                    'data': {
                        'chatId': 1,
                        'text': 'Hello!',
                    },
                },
            ),
            {
                2: [
                    {
                        'type': 'newUnreadCount',
                        'data': {
                            'chatId': 1,
                            'unreadCount': 2,
                        },
                    },
                    {
                        'type': 'newChatMessage',
                        'data': {
                            'id': 2,
                            'chatId': 1,
                            'userId': 1,
                            'text': 'Hello!',
                            'isRead': False,
                            'storageId': None,
                            'creatingDatetime': anything,
                        },
                    },
                ],
                1: [
                    {
                        'type': 'newChatMessage',
                        'data': {
                            'id': 2,
                            'chatId': 1,
                            'userId': 1,
                            'text': 'Hello!',
                            'isRead': False,
                            'storageId': None,
                            'creatingDatetime': anything,
                        },
                    },
                ],
            },
        ),
    ]

    new_chat_message_typing_input_and_output = [
        (
            (
                ORMObjects.users[0],
                {
                    'type': 'newChatMessageTyping',
                    'data': {
                        'chatId': 1,
                    },
                },
            ),
            {
                2: [
                    {
                        'type': 'newChatMessageTyping',
                        'data': {
                            'chatId': 1,
                            'userId': 1,
                        },
                    },
                ],
            },
        ),
    ]

    chat_message_was_read_input_and_output = [
        (
            (
                ORMObjects.users[1],
                {
                    'type': 'chatMessageWasRead',
                    'data': {
                        'chatId': 1,
                        'chatMessageId': 2,
                    },
                },
            ),
            {
                2: [
                    {
                        'type': 'newUnreadCount',
                        'data': {
                            'chatId': 1,
                            'unreadCount': 0,
                        },
                    },
                ],
                1: [
                    {
                        'type': 'readChatMessages',
                        'data': {
                            'chatId': 1,
                            'chatMessagesIds': [1, 2],
                        },
                    },
                ],
            },
        ),
    ]

    all_input_and_output = (online_status_tracing_adding_input_and_output +
                            new_chat_input_and_output +   # type: ignore
                            new_chat_message_input_and_output +
                            new_chat_message_typing_input_and_output +
                            chat_message_was_read_input_and_output)

    new_chat_input_and_raises = [
        (
            (
                ORMObjects.users[0],
                {
                    'type': 'newChat',
                    'data': {
                        'usersIds': [1, 2],
                    },
                },
            ),
            ValueError,  # the chat already exists
        ),
    ]

    new_chat_message_input_and_raises = [
        (
            (
                ORMObjects.users[2],
                {
                    'type': 'newChatMessage',
                    'data': {
                        'chatId': 1,
                        'text': 'Hi! Can I?',
                    },
                },
            ),
            PermissionError,
        ),
    ]

    new_chat_message_typing_input_and_raises = [
        (
            (
                ORMObjects.users[2],
                {
                    'type': 'newChatMessageTyping',
                    'data': {
                        'chatId': 1,
                    },
                },
            ),
            PermissionError,
        ),
    ]

    chat_message_was_read_input_and_raises = [
        (
            (
                ORMObjects.users[2],
                {
                    'type': 'chatMessageWasRead',
                    'data': {
                        'chatId': 1,
                        'chatMessageId': 100,
                    },
                },
            ),
            PermissionError,
        ),
    ]

    all_input_and_raises = (new_chat_input_and_raises +
                            new_chat_message_input_and_raises +  # type: ignore
                            new_chat_message_typing_input_and_raises +
                            chat_message_was_read_input_and_raises)

    new_connects = [
        (
            ORMObjects.users[0],
            {
                2: [
                    {
                        'type': 'interlocutorsOnlineStatuses',
                        'data': {
                            1: True,
                        },
                    },
                ],
                3: [
                    {
                        'type': 'interlocutorsOnlineStatuses',
                        'data': {
                            1: True,
                        },
                    },
                ],
                1: [
                    {
                        'type': 'interlocutorsOnlineStatuses',
                        'data': {
                            2: True,
                        },
                    },
                ],
            },
        ),
    ]

    full_disconnects = [
        (
            ORMObjects.users[0],
            {
                2: [
                    {
                        'type': 'interlocutorsOnlineStatuses',
                        'data': {
                            1: False,
                        },
                    },
                ],
                3: [
                    {
                        'type': 'interlocutorsOnlineStatuses',
                        'data': {
                            1: False,
                        },
                    },
                ],
            },
        ),
    ]

    raw_and_handled_texts = [
        (
            'Hi! 1 2 3\n1 2 3',
            'Hi! 1 2 3\n1 2 3',
        ),
        (
            '   Hello!   How are u??\n  \n\n   My name is Danil!  \n',
            'Hello! How are u??\nMy name is Danil!',
        ),
    ]
