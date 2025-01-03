from db.models import (
    User,
    Chat,
    ChatMessage,
    UserChatMatch,
    UnreadCount,
)

__all__ = (
    'ORMObjects',
    'SetForTest',
)


class Params:

    EMAIL = 'email1@mail.ru'
    UNREAD_COUNT = 5
    STORAGE_ID = 7


class ORMObjects:

    users = [
        User(
            _email=Params.EMAIL,
        ),
        User(
            _email='email2@mail.ru',
        ),
        User(
            _email='email3@mail.ru',
        ),
    ]

    chats = [
        Chat(),
        Chat(),
        Chat(),
    ]

    chat_messages = [
        ChatMessage(
            user_id=1,
            chat_id=1,
            text='Hello!',
            storage_id=Params.STORAGE_ID,
        ),
        ChatMessage(
            user_id=2,
            chat_id=1,
            text='Hello too!',
        ),
    ]

    user_chat_matches = [
        UserChatMatch(
            user_id=1,
            chat_id=1,
        ),
        UserChatMatch(
            user_id=2,
            chat_id=1,
        ),

        UserChatMatch(
            user_id=2,
            chat_id=2,
        ),
        UserChatMatch(
            user_id=3,
            chat_id=2,
        ),

        UserChatMatch(
            user_id=1,
            chat_id=3,
        ),
    ]

    unread_counts = [
        UnreadCount(
            _user_chat_match_id=1,
            _value=Params.UNREAD_COUNT,
        ),
        UnreadCount(
            _user_chat_match_id=2,
        ),

        UnreadCount(
            _user_chat_match_id=3,
        ),
        UnreadCount(
            _user_chat_match_id=4,
        ),
    ]

    all = users + chats + chat_messages + user_chat_matches + unread_counts  # type: ignore


class UserSetForTest:

    by_email = [
        (
            Params.EMAIL,
            ORMObjects.users[0],
        ),
    ]

    email_is_already_taken = [
        (
            Params.EMAIL,
            True,
        ),
        (
            'whatafu...??',
            False,
        )
    ]

    chats = [
        (
            ORMObjects.users[0],
            [
                ORMObjects.chats[0],
                ORMObjects.chats[2],
            ],
        ),
        (
            ORMObjects.users[1],
            [
                ORMObjects.chats[0],
                ORMObjects.chats[1],
            ],
        ),
    ]


class ChatSetForTest:

    users = [
        (
            ORMObjects.chats[0],
            [
                ORMObjects.users[0],
                ORMObjects.users[1],
            ],
        ),
        (
            ORMObjects.chats[1],
            [
                ORMObjects.users[1],
                ORMObjects.users[2],
            ],
        )
    ]

    unread_messages_of_user = [
        (
            ORMObjects.chats[0],
            ORMObjects.users[0],
            [
                ORMObjects.chat_messages[1],
            ],
        ),
        (
            ORMObjects.chats[0],
            ORMObjects.users[1],
            [
                ORMObjects.chat_messages[0],
            ],
        ),
        (
            ORMObjects.chats[1],
            ORMObjects.users[1],
            [],
        ),
    ]

    interlocutor_of_user = [
        (
            ORMObjects.chats[0],
            ORMObjects.users[0],
            ORMObjects.users[1],
        ),
        (
            ORMObjects.chats[1],
            ORMObjects.users[2],
            ORMObjects.users[1],
        ),
    ]

    interlocutor_of_user_raises_value_error = [
        (
            ORMObjects.chats[2],
            ORMObjects.users[0],
        ),
    ]

    unread_count_of_user = [
        (
            ORMObjects.chats[0],
            ORMObjects.users[0],
            Params.UNREAD_COUNT,
        ),
        (
            ORMObjects.chats[1],
            ORMObjects.users[1],
            0,
        ),
    ]

    unread_count_of_user_raises_permission_error = [
        (
            ORMObjects.chats[1],
            ORMObjects.users[0],
        ),
        (
            ORMObjects.chats[0],
            ORMObjects.users[2],
        ),
    ]


class ChatMessageSetForTest:
    by_storage_id = [
        (
            Params.STORAGE_ID,
            ORMObjects.chat_messages[0],
        ),
    ]


class UserChatMatchSetForTest:

    chat_if_user_has_access = [
        (
            ORMObjects.chats[0],
            ORMObjects.users[0],
        ),
        (
            ORMObjects.chats[0],
            ORMObjects.users[1],
        ),

        (
            ORMObjects.chats[1],
            ORMObjects.users[1],
        ),
        (
            ORMObjects.chats[1],
            ORMObjects.users[2],
        ),
    ]

    chat_if_user_has_access_raises_permission_error = [
        (
            ORMObjects.chats[1],
            ORMObjects.users[0],
        ),

        (
            ORMObjects.chats[0],
            ORMObjects.users[2],
        ),
    ]

    users_of_chat = ChatSetForTest.users

    chats_of_user = UserSetForTest.chats

    interlocutor_of_user_of_chat = ChatSetForTest.interlocutor_of_user

    private_chat_between_users = [
        (
            ORMObjects.users[0],
            ORMObjects.users[1],
            ORMObjects.chats[0],
        ),
        (
            ORMObjects.users[1],
            ORMObjects.users[2],
            ORMObjects.chats[1],
        ),
    ]

    private_chat_between_users_raises_value_error = [
        (
            ORMObjects.users[0],
            ORMObjects.users[2],
        ),
    ]

    all_interlocutors_of_user = [
        (
            ORMObjects.users[0],
            [
                ORMObjects.users[1],
            ],
        ),
        (
            ORMObjects.users[1],
            [
                ORMObjects.users[0],
                ORMObjects.users[2],
            ],
        ),
    ]

    unread_count_of_user_of_chat = ChatSetForTest.unread_count_of_user

    unread_count_of_user_of_chat_raises_permission_error = ChatSetForTest.unread_count_of_user_raises_permission_error


class SetForTest:

    User = UserSetForTest
    Chat = ChatSetForTest
    ChatMessage = ChatMessageSetForTest
    UserChatMatch = UserChatMatchSetForTest
