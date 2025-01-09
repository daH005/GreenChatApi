from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_csrf_token,
)
from io import BytesIO
from copy import deepcopy

from config import EMAIL_PASS_CODE
from db.models import (
    User,
    Chat,
    ChatMessage,
    UserChatMatch,
    UnreadCount,
)
from http_.avatars.blueprint import _DEFAULT_AVATAR_PATH
from http_.backgrounds.blueprint import _DEFAULT_BACKGROUND_PATH
from _tests.common.anything_place import anything

__all__ = (
    'Params',
    'ORMObjects',
    'SetForTest',
)


class Params:

    class UrlsAndMethods:

        USER_LOGIN_EMAIL_CHECK = '/user/login/email/check', 'GET'
        USER_LOGIN_EMAIL_CODE_CHECK = '/user/login/email/code/check', 'GET'
        USER_LOGIN_EMAIL_CODE_SEND = '/user/login/email/code/send', 'POST'
        USER_LOGIN = '/user/login', 'POST'
        USER_LOGOUT = '/user/logout', 'POST'
        USER_REFRESH_ACCESS = '/user/refreshAccess', 'POST'
        USER_INFO_EDIT = '/user/info/edit', 'PUT'
        USER_INFO = '/user/info', 'GET'
        USER_CHATS = '/user/chats', 'GET'
        USER_AVATAR_EDIT = '/user/avatar/edit', 'PUT'
        USER_AVATAR = '/user/avatar', 'GET'
        USER_BACKGROUND_EDIT = '/user/background/edit', 'PUT'
        USER_BACKGROUND = '/user/background', 'GET'

        CHAT_HISTORY = '/chat/history', 'GET'
        CHAT_MESSAGES_FILES_SAVE = '/chat/messages/files/save', 'POST'
        CHAT_MESSAGES_FILES_NAMES = '/chat/messages/files/names', 'GET'
        CHAT_MESSAGES_FILES_GET = '/chat/messages/files/get', 'GET'

    STORAGE_ID = 50000
    UNREAD_COUNT = 70

    EMAIL_WITH_CODE = 'email@gmail.com'
    EMAIL_CODE = 5050

    FIRST_NAME = 'fname'
    LAST_NAME = 'lname'

    AVATAR_BYTES = b'\x89PNG\r\n\x1a\n\x00\x00\x00\r' \
                   b'IHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x03' \
                   b'PLTE\x00\x00\x00\xa7z=\xda\x00\x00\x00\x01' \
                   b'tRNS\x00@\xe6\xd8f\x00\x00\x00\n' \
                   b'IDAT\x08\xd7c`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'
    BACKGROUND_BYTES = AVATAR_BYTES

    FILE_CONTENTS = [
        b'file1',
        b'print(123)',
    ]
    FILES = [
        (
            BytesIO(FILE_CONTENTS[0]),
            'file1.txt',
        ),
        (
            BytesIO(FILE_CONTENTS[1]),
            'file2.py',
        ),
    ]

    AVATAR_MAX_BYTES = bytes(300)
    BACKGROUND_MAX_BYTES = bytes(1000)
    FILES_MAX_BYTES = bytes(500)

    user = dict(
        _id=500000,
        _email='user1@mail.ru',
    )

    ACCESS_TOKEN = create_access_token(user['_email'])
    ACCESS_CSRF_TOKEN = get_csrf_token(ACCESS_TOKEN)

    REFRESH_TOKEN = create_refresh_token(user['_email'])
    REFRESH_CSRF_TOKEN = get_csrf_token(REFRESH_TOKEN)

    SECOND_ACCESS_TOKEN = create_access_token(EMAIL_WITH_CODE)
    SECOND_ACCESS_CSRF_TOKEN = get_csrf_token(SECOND_ACCESS_TOKEN)

    chat_messages = [
        dict(
            _user_id=user['_id'],
            _chat_id=1,
            _text='Hello_1!',
        ),
        dict(
            _user_id=user['_id'],
            _chat_id=1,
            _text='Hello_2!',
            _storage_id=STORAGE_ID,
        ),
        dict(
            _user_id=user['_id'],
            _chat_id=1,
            _text='Hello_3!',
        ),
    ]


class ORMObjects:

    users = [
        User(**Params.user),
    ]

    chats = [
        Chat(),
        Chat(),
    ]

    chat_messages = [
        ChatMessage(**Params.chat_messages[0]),
        ChatMessage(**Params.chat_messages[1]),
        ChatMessage(**Params.chat_messages[2]),
    ]

    user_chat_matches = [
        UserChatMatch(
            _user_id=Params.user['_id'],
            _chat_id=1,
        ),
    ]

    unread_counts = [
        UnreadCount(
            _user_chat_match_id=1,
            _value=Params.UNREAD_COUNT,
        ),
    ]

    all = users + chats + chat_messages + user_chat_matches + unread_counts  # type: ignore


class SetForTest:

    user_login_email_check = [
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CHECK[1],
            query_string={
                'email': 'anyemail@yandex.ru',
            },

            expected_status_code=200,
            expected_json_dict={
                'isAlreadyTaken': False,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CHECK[1],
            query_string={
                'email': Params.user['_email'],
            },

            expected_status_code=200,
            expected_json_dict={
                'isAlreadyTaken': True,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CHECK[1],

            expected_status_code=400,
        ),
    ]

    user_login_email_code_check = [
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={
                'email': 'blabla@mail.ru',
                'code': 1001,
            },

            expected_status_code=200,
            expected_json_dict={
                'codeIsValid': False,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={
                'email': Params.EMAIL_WITH_CODE,
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=200,
            expected_json_dict={
                'codeIsValid': True,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={
                'email': Params.EMAIL_WITH_CODE,
                'code': Params.EMAIL_CODE * 1000,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={
                'email': Params.EMAIL_WITH_CODE,
                'code': 'text',
            },

            expected_status_code=400,
        ),
    ]

    user_login_email_code_send = [
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[1],
            json_dict={
                'email': Params.user['_email'],
            },

            expected_status_code=202,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[1],
            json_dict={
                'email': 'what',
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[1],
            json_dict={
                'email': Params.user['_email'],
            },

            expected_status_code=409,
        ),
    ]

    user_login = [
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': Params.EMAIL_WITH_CODE,
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=201,
            expected_set_cookie={
                'access_token_cookie': anything,
                'csrf_access_token': anything,
                'refresh_token_cookie': anything,
                'csrf_refresh_token': anything,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': Params.EMAIL_WITH_CODE,
                'code': EMAIL_PASS_CODE,
            },

            expected_status_code=200,
            expected_set_cookie={
                'access_token_cookie': anything,
                'csrf_access_token': anything,
                'refresh_token_cookie': anything,
                'csrf_refresh_token': anything,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={},

            expected_status_code=400,
        ),
    ]

    user_logout = [
        dict(
            url=Params.UrlsAndMethods.USER_LOGOUT[0],
            method=Params.UrlsAndMethods.USER_LOGOUT[1],
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_set_cookie={
                'access_token_cookie': anything,
                'csrf_access_token': anything,
                'refresh_token_cookie': anything,
                'csrf_refresh_token': anything,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGOUT[0],
            method=Params.UrlsAndMethods.USER_LOGOUT[1],
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': 'what',
            },

            expected_status_code=401,
            expected_json_dict=anything,
        ),
    ]

    user_refresh_access = [
        dict(
            url=Params.UrlsAndMethods.USER_REFRESH_ACCESS[0],
            method=Params.UrlsAndMethods.USER_REFRESH_ACCESS[1],
            cookies={
                'refresh_token_cookie': Params.REFRESH_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.REFRESH_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_set_cookie={
                'access_token_cookie': anything,
                'csrf_access_token': anything,
                'refresh_token_cookie': anything,
                'csrf_refresh_token': anything,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_REFRESH_ACCESS[0],
            method=Params.UrlsAndMethods.USER_REFRESH_ACCESS[1],
            cookies={
                'refresh_token_cookie': Params.REFRESH_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.REFRESH_CSRF_TOKEN,
            },

            expected_status_code=401,  # check blacklist
            expected_json_dict=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_REFRESH_ACCESS[0],
            method=Params.UrlsAndMethods.USER_REFRESH_ACCESS[1],
            cookies={
                'refresh_token_cookie': create_refresh_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': 'what',
            },

            expected_status_code=401,
            expected_json_dict=anything,
        ),
    ]

    user_info_edit = [
        dict(
            url=Params.UrlsAndMethods.USER_INFO_EDIT[0],
            method=Params.UrlsAndMethods.USER_INFO_EDIT[1],
            json_dict={
                'firstName': Params.FIRST_NAME,
                'lastName': Params.LAST_NAME,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_INFO_EDIT[0],
            method=Params.UrlsAndMethods.USER_INFO_EDIT[1],
            json_dict={
                'firstName': '',
                'lastName': ''
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_INFO_EDIT[0],
            method=Params.UrlsAndMethods.USER_INFO_EDIT[1],
            json_dict={},
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_INFO_EDIT[0],
            method=Params.UrlsAndMethods.USER_INFO_EDIT[1],
            json_dict={
                'firstName': 'fff',
                'lastName': 'fff'
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_dict=anything,
        ),
    ]

    user_info = [
        dict(
            url=Params.UrlsAndMethods.USER_INFO[0],
            method=Params.UrlsAndMethods.USER_INFO[1],
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_dict={
                'id': Params.user['_id'],
                'email': Params.user['_email'],
                'firstName': Params.FIRST_NAME,
                'lastName': Params.LAST_NAME,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_INFO[0],
            method=Params.UrlsAndMethods.USER_INFO[1],
            query_string={
                'userId': Params.user['_id'] + 1,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_dict={
                'id': Params.user['_id'] + 1,
                'firstName': User._first_name.default.arg,
                'lastName': User._last_name.default.arg,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_INFO[0],
            method=Params.UrlsAndMethods.USER_INFO[1],
            query_string={
                'userId': 'text',
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_INFO[0],
            method=Params.UrlsAndMethods.USER_INFO[1],
            query_string={
                'userId': Params.user['_id'],
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_dict=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_INFO[0],
            method=Params.UrlsAndMethods.USER_INFO[1],
            query_string={
                'userId': 1333,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=404,
        ),
    ]

    user_chats = [
        dict(
            url=Params.UrlsAndMethods.USER_CHATS[0],
            method=Params.UrlsAndMethods.USER_CHATS[1],
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_dict={
                'chats': [
                    {
                        'id': 1,
                        'name': None,
                        'isGroup': False,
                        'lastMessage': {
                            'id': 3,
                            'chatId': 1,
                            'userId': Params.user['_id'],
                            'text': Params.chat_messages[-1]['_text'],
                            'storageId': None,
                            'isRead': False,
                            'creatingDatetime': anything,
                        },
                        'userIds': [Params.user['_id']],
                        'unreadCount': Params.UNREAD_COUNT,
                    }
                ],
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_CHATS[0],
            method=Params.UrlsAndMethods.USER_CHATS[1],
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_dict=anything,
        ),
    ]

    user_avatar_edit = [
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR_EDIT[0],
            method=Params.UrlsAndMethods.USER_AVATAR_EDIT[1],
            data=Params.AVATAR_BYTES,
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'Content-Type': 'image/png',
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR_EDIT[0],
            method=Params.UrlsAndMethods.USER_AVATAR_EDIT[1],
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'Content-Type': 'image/png',
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR_EDIT[0],
            method=Params.UrlsAndMethods.USER_AVATAR_EDIT[1],
            data=Params.AVATAR_BYTES,
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR_EDIT[0],
            method=Params.UrlsAndMethods.USER_AVATAR_EDIT[1],
            data=b'blabla',
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'Content-Type': 'image/png',
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR_EDIT[0],
            method=Params.UrlsAndMethods.USER_AVATAR_EDIT[1],
            data=Params.AVATAR_BYTES,
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_dict=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR_EDIT[0],
            method=Params.UrlsAndMethods.USER_AVATAR_EDIT[1],
            data=Params.AVATAR_MAX_BYTES * 2,
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=413,
        ),
    ]

    user_avatar = [
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR[0],
            method=Params.UrlsAndMethods.USER_AVATAR[1],
            query_string={
                'userId': Params.user['_id'],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_content=Params.AVATAR_BYTES,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR[0],
            method=Params.UrlsAndMethods.USER_AVATAR[1],
            query_string={
                'userId': 1333,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_content=_DEFAULT_AVATAR_PATH.read_bytes(),
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR[0],
            method=Params.UrlsAndMethods.USER_AVATAR[1],
            query_string={
                'userId': Params.user['_id'],
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_content=anything,
        ),
    ]

    user_background_edit = [
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[1],
            data=Params.BACKGROUND_BYTES,
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'Content-Type': 'image/png',
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[1],
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'Content-Type': 'image/png',
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[1],
            data=Params.BACKGROUND_BYTES,
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[1],
            data=b'blabla',
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'Content-Type': 'image/png',
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[1],
            data=Params.BACKGROUND_BYTES,
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_dict=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[1],
            data=Params.BACKGROUND_MAX_BYTES * 2,
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=413,
        ),
    ]

    user_background = [
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND[1],
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_content=Params.BACKGROUND_BYTES,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND[1],
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_content=_DEFAULT_BACKGROUND_PATH.read_bytes(),
        ),
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND[1],
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_content=anything,
        ),
    ]

    chat_history = [
        dict(
            url=Params.UrlsAndMethods.CHAT_HISTORY[0],
            method=Params.UrlsAndMethods.CHAT_HISTORY[1],
            query_string={
                'chatId': 1,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_dict={
                'messages': [
                    {
                        'id': 3,
                        'chatId': 1,
                        'userId': Params.user['_id'],
                        'text': Params.chat_messages[2]['_text'],
                        'storageId': None,
                        'isRead': False,
                        'creatingDatetime': anything,
                    },
                    {
                        'id': 2,
                        'chatId': 1,
                        'userId': Params.user['_id'],
                        'text': Params.chat_messages[1]['_text'],
                        'storageId': Params.STORAGE_ID,
                        'isRead': False,
                        'creatingDatetime': anything,
                    },
                    {
                        'id': 1,
                        'chatId': 1,
                        'userId': Params.user['_id'],
                        'text': Params.chat_messages[0]['_text'],
                        'storageId': None,
                        'isRead': False,
                        'creatingDatetime': anything,
                    },
                ],
            },
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_HISTORY[0],
            method=Params.UrlsAndMethods.CHAT_HISTORY[1],
            query_string={
                'chatId': 2,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=403,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_HISTORY[0],
            method=Params.UrlsAndMethods.CHAT_HISTORY[1],
            query_string={
                'chatId': 3333,  # instead of 404
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=403,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_HISTORY[0],
            method=Params.UrlsAndMethods.CHAT_HISTORY[1],
            query_string={
                'chatId': 1,
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_dict=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_HISTORY[0],
            method=Params.UrlsAndMethods.CHAT_HISTORY[1],
            query_string={
                'chatId': 'what',
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
    ]

    chat_messages_files_save = [
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_SAVE[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_SAVE[1],
            data={
                'files': deepcopy(Params.FILES),
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_dict={
                'storageId': Params.STORAGE_ID,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_SAVE[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_SAVE[1],
            data={
                'files': deepcopy(Params.FILES),
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_content=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_SAVE[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_SAVE[1],
            data={
                'files': [
                    (
                        BytesIO(Params.FILES_MAX_BYTES[:len(Params.FILES_MAX_BYTES) // 4]),
                        'large1.txt',
                    ),
                    (
                        BytesIO(Params.FILES_MAX_BYTES),
                        'large2.txt',
                    ),
                ],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=413,
        ),
    ]

    chat_messages_files_names = [
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[1],
            query_string={
                'storageId': Params.STORAGE_ID,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_dict={
                'filenames': [
                    Params.FILES[1][1],
                    Params.FILES[0][1],
                ],
            },
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[1],
            query_string={
                'storageId': '',
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[1],
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[1],
            query_string={
                'storageId': Params.STORAGE_ID,
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_dict=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[1],
            query_string={
                'storageId': 3333,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=404,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_NAMES[1],
            query_string={
                'storageId': Params.STORAGE_ID,
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=403,
        ),
    ]

    chat_messages_files_get = [
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[1],
            query_string={
                'storageId': Params.STORAGE_ID,
                'filename': Params.FILES[0][1],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_content=Params.FILE_CONTENTS[0],
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[1],
            query_string={
                'storageId': Params.STORAGE_ID,
                'filename': Params.FILES[1][1],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_content=Params.FILE_CONTENTS[1],
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[1],
            query_string={
                'storageId': '',
                'filename': Params.FILES[0][1],
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[1],
            query_string={
                'storageId': Params.STORAGE_ID,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[1],
            query_string={
                'storageId': Params.STORAGE_ID,
                'filename': Params.FILES[1][1],
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_content=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[1],
            query_string={
                'storageId': Params.STORAGE_ID,
                'filename': Params.FILES[0][1],
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=403,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[1],
            query_string={
                'storageId': Params.STORAGE_ID,
                'filename': 'blabla.txt',
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=404,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES_FILES_GET[1],
            query_string={
                'storageId': 13333,
                'filename': 'blabla.txt',
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=404,
        ),
    ]
