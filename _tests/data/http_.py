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

    class Urls:

        USER_LOGIN_EMAIL_CHECK = '/user/login/email/check'
        USER_LOGIN_EMAIL_CODE_CHECK = '/user/login/email/code/check'
        USER_LOGIN_EMAIL_CODE_SEND = '/user/login/email/code/send'
        USER_LOGIN = '/user/login'
        USER_LOGOUT = '/user/logout'
        USER_REFRESH_ACCESS = '/user/refreshAccess'
        USER_INFO_EDIT = '/user/info/edit'
        USER_INFO = '/user/info'
        USER_CHATS = '/user/chats'
        USER_AVATAR_EDIT = '/user/avatar/edit'
        USER_AVATAR = '/user/avatar'
        USER_BACKGROUND_EDIT = '/user/background/edit'
        USER_BACKGROUND = '/user/background'

        CHAT_HISTORY = '/chat/history'
        CHAT_MESSAGES_FILES_SAVE = '/chat/messages/files/save'
        CHAT_MESSAGES_FILES_NAMES = '/chat/messages/files/names'
        CHAT_MESSAGES_FILES_GET = '/chat/messages/files/get'

    STORAGE_ID = 100
    UNREAD_COUNT = 70

    EMAIL_WITH_CODE = 'email@gmail.com'
    EMAIL_CODE = 5050

    FIRST_NAME = 'fname'
    LAST_NAME = 'lname'

    AVATAR_BYTES = b'avatar'
    BACKGROUND_BYTES = b'background'

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
            url=Params.Urls.USER_LOGIN_EMAIL_CHECK,
            method='GET',
            query_string={
                'email': 'anyemail@yandex.ru',
            },

            expected_status_code=200,
            expected_json_dict={
                'isAlreadyTaken': False,
            },
        ),
        dict(
            url=Params.Urls.USER_LOGIN_EMAIL_CHECK,
            method='GET',
            query_string={
                'email': Params.user['_email'],
            },

            expected_status_code=200,
            expected_json_dict={
                'isAlreadyTaken': True,
            },
        ),
        dict(
            url=Params.Urls.USER_LOGIN_EMAIL_CHECK,
            method='GET',

            expected_status_code=400,
            expected_json_dict={
                'status': 400,
            },
        ),
    ]

    user_login_email_code_check = [
        dict(
            url=Params.Urls.USER_LOGIN_EMAIL_CODE_CHECK,
            method='GET',
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
            url=Params.Urls.USER_LOGIN_EMAIL_CODE_CHECK,
            method='GET',
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
            url=Params.Urls.USER_LOGIN_EMAIL_CODE_CHECK,
            method='GET',

            expected_status_code=400,
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.USER_LOGIN_EMAIL_CODE_CHECK,
            method='GET',
            query_string={
                'email': Params.EMAIL_WITH_CODE,
                'code': Params.EMAIL_CODE * 1000,
            },

            expected_status_code=400,
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.USER_LOGIN_EMAIL_CODE_CHECK,
            method='GET',
            query_string={
                'email': Params.EMAIL_WITH_CODE,
                'code': 'text',
            },

            expected_status_code=400,
            expected_json_dict={
                'status': 400,
            },
        ),
    ]

    user_login_email_code_send = [
        dict(
            url=Params.Urls.USER_LOGIN_EMAIL_CODE_SEND,
            method='POST',
            json_dict={
                'email': Params.user['_email'],
            },

            expected_status_code=200,
            expected_json_dict={
                'status': 200,
            },
        ),
        dict(
            url=Params.Urls.USER_LOGIN_EMAIL_CODE_SEND,
            method='POST',
            json_dict={
                'email': 'what',
            },

            expected_status_code=400,
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.USER_LOGIN_EMAIL_CODE_SEND,
            method='POST',
            json_dict={
                'email': Params.user['_email'],
            },

            expected_status_code=409,
            expected_json_dict={
                'status': 409,
            },
        ),
    ]

    user_login = [
        dict(
            url=Params.Urls.USER_LOGIN,
            method='POST',
            json_dict={
                'email': Params.EMAIL_WITH_CODE,
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=201,
            expected_json_dict={
                'status': 201,
            },
            expected_set_cookie={
                'access_token_cookie': anything,
                'csrf_access_token': anything,
                'refresh_token_cookie': anything,
                'csrf_refresh_token': anything,
            },
        ),
        dict(
            url=Params.Urls.USER_LOGIN,
            method='POST',
            json_dict={
                'email': Params.EMAIL_WITH_CODE,
                'code': EMAIL_PASS_CODE,
            },

            expected_status_code=200,
            expected_json_dict={
                'status': 200,
            },
            expected_set_cookie={
                'access_token_cookie': anything,
                'csrf_access_token': anything,
                'refresh_token_cookie': anything,
                'csrf_refresh_token': anything,
            },
        ),
        dict(
            url=Params.Urls.USER_LOGIN,
            method='POST',
            json_dict={},

            expected_status_code=400,
            expected_json_dict={
                'status': 400,
            },
        ),
    ]

    user_logout = [
        dict(
            url=Params.Urls.USER_LOGOUT,
            method='POST',
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_dict={
                'status': 200,
            },
            expected_set_cookie={
                'access_token_cookie': anything,
                'csrf_access_token': anything,
                'refresh_token_cookie': anything,
                'csrf_refresh_token': anything,
            },
        ),
        dict(
            url=Params.Urls.USER_LOGOUT,
            method='POST',
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
            url=Params.Urls.USER_REFRESH_ACCESS,
            method='POST',
            cookies={
                'refresh_token_cookie': Params.REFRESH_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.REFRESH_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_dict={
                'status': 200,
            },
            expected_set_cookie={
                'access_token_cookie': anything,
                'csrf_access_token': anything,
                'refresh_token_cookie': anything,
                'csrf_refresh_token': anything,
            },
        ),
        dict(
            url=Params.Urls.USER_REFRESH_ACCESS,
            method='POST',
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
            url=Params.Urls.USER_REFRESH_ACCESS,
            method='POST',
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
            url=Params.Urls.USER_INFO_EDIT,
            method='PUT',
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
            expected_json_dict={
                'status': 200,
            },
        ),
        dict(
            url=Params.Urls.USER_INFO_EDIT,
            method='PUT',
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
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.USER_INFO_EDIT,
            method='PUT',
            json_dict={},
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.USER_INFO_EDIT,
            method='PUT',
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
            url=Params.Urls.USER_INFO,
            method='GET',
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
            url=Params.Urls.USER_INFO,
            method='GET',
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
            url=Params.Urls.USER_INFO,
            method='GET',
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
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.USER_INFO,
            method='GET',
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
            url=Params.Urls.USER_INFO,
            method='GET',
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
            expected_json_dict={
                'status': 404,
            },
        ),
    ]

    user_chats = [
        dict(
            url=Params.Urls.USER_CHATS,
            method='GET',
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
            url=Params.Urls.USER_CHATS,
            method='GET',
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
            url=Params.Urls.USER_AVATAR_EDIT,
            method='PUT',
            data=Params.AVATAR_BYTES,
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_dict={
                'status': 200,
            },
        ),
        dict(
            url=Params.Urls.USER_AVATAR_EDIT,
            method='PUT',
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
            url=Params.Urls.USER_AVATAR_EDIT,
            method='PUT',
            data=Params.AVATAR_MAX_BYTES * 2,
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=413,
            expected_json_dict={
                'status': 413,
            },
        ),
    ]

    user_avatar = [
        dict(
            url=Params.Urls.USER_AVATAR,
            method='GET',
            query_string={
                'userId':Params.user['_id'],
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
            url=Params.Urls.USER_AVATAR,
            method='GET',
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
            url=Params.Urls.USER_AVATAR,
            method='GET',
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
            url=Params.Urls.USER_BACKGROUND_EDIT,
            method='PUT',
            data=Params.BACKGROUND_BYTES,
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_dict={
                'status': 200,
            },
        ),
        dict(
            url=Params.Urls.USER_BACKGROUND_EDIT,
            method='PUT',
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
            url=Params.Urls.USER_BACKGROUND_EDIT,
            method='PUT',
            data=Params.BACKGROUND_MAX_BYTES * 2,
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=413,
            expected_json_dict={
                'status': 413,
            },
        ),
    ]

    user_background = [
        dict(
            url=Params.Urls.USER_BACKGROUND,
            method='GET',
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
            url=Params.Urls.USER_BACKGROUND,
            method='GET',
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
            url=Params.Urls.USER_BACKGROUND,
            method='GET',
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
            url=Params.Urls.CHAT_HISTORY,
            method='GET',
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
            url=Params.Urls.CHAT_HISTORY,
            method='GET',
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
            expected_json_dict={
                'status': 403,
            },
        ),
        dict(
            url=Params.Urls.CHAT_HISTORY,
            method='GET',
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
            expected_json_dict={
                'status': 403,
            },
        ),
        dict(
            url=Params.Urls.CHAT_HISTORY,
            method='GET',
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
            url=Params.Urls.CHAT_HISTORY,
            method='GET',
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
            expected_json_dict={
                'status': 400,
            },
        ),
    ]

    chat_messages_files_save = [
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_SAVE,
            method='POST',
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
            url=Params.Urls.CHAT_MESSAGES_FILES_SAVE,
            method='POST',
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
            url=Params.Urls.CHAT_MESSAGES_FILES_SAVE,
            method='POST',
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
            expected_json_dict={
                'status': 413,
            },
        ),
    ]

    chat_messages_files_names = [
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_NAMES,
            method='GET',
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
            url=Params.Urls.CHAT_MESSAGES_FILES_NAMES,
            method='GET',
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
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_NAMES,
            method='GET',
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_NAMES,
            method='GET',
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
            url=Params.Urls.CHAT_MESSAGES_FILES_NAMES,
            method='GET',
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
            expected_json_dict={
                'status': 404,
            },
        ),
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_NAMES,
            method='GET',
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
            expected_json_dict={
                'status': 403,
            },
        ),
    ]

    chat_messages_files_get = [
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_GET,
            method='GET',
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
            url=Params.Urls.CHAT_MESSAGES_FILES_GET,
            method='GET',
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
            url=Params.Urls.CHAT_MESSAGES_FILES_GET,
            method='GET',
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
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_GET,
            method='GET',
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
            expected_json_dict={
                'status': 400,
            },
        ),
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_GET,
            method='GET',
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
            url=Params.Urls.CHAT_MESSAGES_FILES_GET,
            method='GET',
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
            expected_json_dict={
                'status': 403,
            },
        ),
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_GET,
            method='GET',
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
            expected_json_dict={
                'status': 404,
            },
        ),
        dict(
            url=Params.Urls.CHAT_MESSAGES_FILES_GET,
            method='GET',
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
            expected_json_dict={
                'status': 404,
            },
        ),
    ]
