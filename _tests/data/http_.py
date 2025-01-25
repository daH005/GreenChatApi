from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_csrf_token,
)
from io import BytesIO
from copy import deepcopy

from config import EMAIL_PASS_CODE
from common.signals.message import SignalQueueMessage
from db.models import User
from http_.avatars.blueprint import _DEFAULT_AVATAR_PATH
from http_.backgrounds.blueprint import _DEFAULT_BACKGROUND_PATH
from _tests.common.anything_place import anything

__all__ = (
    'Params',
    'SetForTest',
)


class Params:
    class UrlsAndMethods:
        USER_LOGIN = '/user/login', 'POST'
        USER_LOGIN_EMAIL_CHECK = '/user/login/email/check', 'GET'
        USER_LOGIN_EMAIL_CODE_SEND = '/user/login/email/code/send', 'POST'
        USER_LOGIN_EMAIL_CODE_CHECK = '/user/login/email/code/check', 'GET'
        USER_LOGOUT = '/user/logout', 'POST'
        USER_REFRESH_ACCESS = '/user/refreshAccess', 'POST'
        USER_EDIT = '/user/edit', 'PUT'
        USER = '/user', 'GET'
        USER_AVATAR_EDIT = '/user/avatar/edit', 'PUT'
        USER_AVATAR = '/user/avatar', 'GET'
        USER_BACKGROUND_EDIT = '/user/background/edit', 'PUT'
        USER_BACKGROUND = '/user/background', 'GET'

        CHAT_NEW = '/chat/new', 'POST'
        MESSAGE_NEW = '/message/new', 'POST'
        MESSAGE_FILES_UPDATE = '/message/files/update', 'PUT'
        MESSAGE_READ = '/message/read', 'PUT'
        MESSAGE_FILES_NAMES = '/message/files/names', 'GET'
        MESSAGE_FILES_GET = '/message/files/get', 'GET'
        CHAT_UNREAD_COUNT = '/chat/unreadCount', 'GET'
        CHAT_TYPING = '/chat/typing', 'POST'
        CHAT = '/chat', 'GET'
        MESSAGE = '/message', 'GET'
        CHAT_MESSAGES = '/chat/messages', 'GET'

        USER_CHATS = '/user/chats', 'GET'

    ID_START = 50000

    DEFAULT_FIRST_NAME = User._first_name.default.arg
    DEFAULT_LAST_NAME = User._last_name.default.arg

    EMAIL_FOR_CODE = 'blabla@mail.ru'
    EMAIL_CODE = EMAIL_PASS_CODE

    IMAGE_BYTES = b'\x89PNG\r\n\x1a\n\x00\x00\x00\r' \
                  b'IHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x03' \
                  b'PLTE\x00\x00\x00\xa7z=\xda\x00\x00\x00\x01' \
                  b'tRNS\x00@\xe6\xd8f\x00\x00\x00\n' \
                  b'IDAT\x08\xd7c`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'

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

    EMAILS = [
        'user1@mail.ru',
        'user2@mail.ru',
        'user3@mail.ru',
        'user4@mail.ru',
        'user5@mail.ru',
    ]

    ACCESS_TOKEN = create_access_token(EMAILS[0])
    ACCESS_CSRF_TOKEN = get_csrf_token(ACCESS_TOKEN)

    REFRESH_TOKEN = create_refresh_token(EMAILS[0])
    REFRESH_CSRF_TOKEN = get_csrf_token(REFRESH_TOKEN)

    SECOND_ACCESS_TOKEN = create_access_token(EMAILS[1])
    SECOND_ACCESS_CSRF_TOKEN = get_csrf_token(SECOND_ACCESS_TOKEN)

    NEW_FIRST_NAME = 'fname'
    NEW_LAST_NAME = 'lname'

    MESSAGE_TEXTS = [
        'Hello1',
        'Hello2',
        'Hello3',
    ]

    BIG_TEXT = '0' * 20_000
    CUT_BIG_TEXT = BIG_TEXT[:10_000]


class SetForTest:
    user_login = [
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={},

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': 'a@a',
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': Params.EMAIL_FOR_CODE,
                'code': 10000,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': Params.EMAIL_FOR_CODE,
                'code': 'text',
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': Params.EMAILS[0],
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
                'email': Params.EMAILS[1],
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=201,
            expected_set_cookie=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': Params.EMAILS[2],
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=201,
            expected_set_cookie=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': Params.EMAILS[3],
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=201,
            expected_set_cookie=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': Params.EMAILS[4],
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=201,
            expected_set_cookie=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN[0],
            method=Params.UrlsAndMethods.USER_LOGIN[1],
            json_dict={
                'email': Params.EMAILS[0],
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=200,
            expected_set_cookie={
                'access_token_cookie': anything,
                'csrf_access_token': anything,
                'refresh_token_cookie': anything,
                'csrf_refresh_token': anything,
            },
        ),
    ]

    user_login_email_code_send = [
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[1],
            json_dict={},

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[1],
            json_dict={
                'email': 'a@a',
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[1],
            json_dict={
                'email': Params.EMAIL_FOR_CODE,
            },

            expected_status_code=202,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_SEND[1],
            json_dict={
                'email': Params.EMAIL_FOR_CODE,
            },

            expected_status_code=409,
        ),
    ]

    user_login_email_code_check = [
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={},

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={
                'email': 'a@a',
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={
                'email': Params.EMAIL_FOR_CODE,
                'code': 10000,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={
                'email': Params.EMAIL_FOR_CODE,
                'code': 'text',
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={
                'email': 'blabla@mail.ru',
                'code': 1001,
            },

            expected_status_code=200,
            expected_json_object={
                'isThat': False,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[0],
            method=Params.UrlsAndMethods.USER_LOGIN_EMAIL_CODE_CHECK[1],
            query_string={
                'email': Params.EMAIL_FOR_CODE,
                'code': Params.EMAIL_CODE,
            },

            expected_status_code=200,
            expected_json_object={
                'isThat': True,
            },
        ),
    ]

    user_logout = [
        dict(
            url=Params.UrlsAndMethods.USER_LOGOUT[0],
            method=Params.UrlsAndMethods.USER_LOGOUT[1],
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
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
    ]

    user_refresh_access = [
        dict(
            url=Params.UrlsAndMethods.USER_REFRESH_ACCESS[0],
            method=Params.UrlsAndMethods.USER_REFRESH_ACCESS[1],
            cookies={
                'refresh_token_cookie': create_refresh_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
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
            expected_json_object=anything,
        ),
    ]

    user_edit = [
        dict(
            url=Params.UrlsAndMethods.USER_EDIT[0],
            method=Params.UrlsAndMethods.USER_EDIT[1],
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
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_EDIT[0],
            method=Params.UrlsAndMethods.USER_EDIT[1],
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
            url=Params.UrlsAndMethods.USER_EDIT[0],
            method=Params.UrlsAndMethods.USER_EDIT[1],
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
            url=Params.UrlsAndMethods.USER_EDIT[0],
            method=Params.UrlsAndMethods.USER_EDIT[1],
            json_dict={
                'firstName': Params.NEW_FIRST_NAME,
                'lastName': Params.NEW_LAST_NAME,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
        ),
    ]

    user = [
        dict(
            url=Params.UrlsAndMethods.USER[0],
            method=Params.UrlsAndMethods.USER[1],
            query_string={
                'userId': Params.ID_START,
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER[0],
            method=Params.UrlsAndMethods.USER[1],
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
            url=Params.UrlsAndMethods.USER[0],
            method=Params.UrlsAndMethods.USER[1],
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
        dict(
            url=Params.UrlsAndMethods.USER[0],
            method=Params.UrlsAndMethods.USER[1],
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_object={
                'id': Params.ID_START,
                'email': Params.EMAILS[0],
                'firstName': Params.NEW_FIRST_NAME,
                'lastName': Params.NEW_LAST_NAME,
                'isOnline': False,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.USER[0],
            method=Params.UrlsAndMethods.USER[1],
            query_string={
                'userId': Params.ID_START + 1,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_object={
                'id': Params.ID_START + 1,
                'firstName': Params.DEFAULT_FIRST_NAME,
                'lastName': Params.DEFAULT_LAST_NAME,
                'isOnline': False,
            },
        ),
    ]

    user_avatar_edit = [
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR_EDIT[0],
            method=Params.UrlsAndMethods.USER_AVATAR_EDIT[1],
            data=Params.IMAGE_BYTES,
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR_EDIT[0],
            method=Params.UrlsAndMethods.USER_AVATAR_EDIT[1],
            data=b'',
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
            data=Params.IMAGE_BYTES,
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
            data=Params.AVATAR_MAX_BYTES * 2,
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=413,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR_EDIT[0],
            method=Params.UrlsAndMethods.USER_AVATAR_EDIT[1],
            data=Params.IMAGE_BYTES,
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'Content-Type': 'image/png',
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
        ),
    ]

    user_avatar = [
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
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR[0],
            method=Params.UrlsAndMethods.USER_AVATAR[1],
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

            expected_status_code=404,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR[0],
            method=Params.UrlsAndMethods.USER_AVATAR[1],
            query_string={},
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_content=Params.IMAGE_BYTES,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_AVATAR[0],
            method=Params.UrlsAndMethods.USER_AVATAR[1],
            query_string={
                'userId': Params.ID_START + 1,
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
    ]

    user_background_edit = [
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[1],
            data=Params.IMAGE_BYTES,
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[1],
            data=b'',
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
            data=Params.IMAGE_BYTES,
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
            data=Params.BACKGROUND_MAX_BYTES * 2,
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=413,
        ),
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND_EDIT[1],
            data=Params.IMAGE_BYTES,
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'Content-Type': 'image/png',
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
        ),
    ]

    user_background = [
        dict(
            url=Params.UrlsAndMethods.USER_BACKGROUND[0],
            method=Params.UrlsAndMethods.USER_BACKGROUND[1],
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_content=anything,
        ),
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
            expected_content=Params.IMAGE_BYTES,
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
    ]

    chat_new = [
        dict(
            url=Params.UrlsAndMethods.CHAT_NEW[0],
            method=Params.UrlsAndMethods.CHAT_NEW[1],
            json_dict={
                'userIds': [Params.ID_START + 1],
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_NEW[0],
            method=Params.UrlsAndMethods.CHAT_NEW[1],
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
            url=Params.UrlsAndMethods.CHAT_NEW[0],
            method=Params.UrlsAndMethods.CHAT_NEW[1],
            json_dict={
                'userIds': [],
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
            url=Params.UrlsAndMethods.CHAT_NEW[0],
            method=Params.UrlsAndMethods.CHAT_NEW[1],
            json_dict={
                'userIds': [Params.ID_START + 1],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object=anything,
            expected_signal_queue_messages=[
                SignalQueueMessage(
                    user_ids=[Params.ID_START, Params.ID_START + 1],
                    message={
                        'type': 'NEW_CHAT',
                        'data': {
                            'chatId': 1,
                        },
                    },
                ),
            ],
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_NEW[0],
            method=Params.UrlsAndMethods.CHAT_NEW[1],
            json_dict={
                'userIds': [Params.ID_START + 2],
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object=anything,
            expected_signal_queue_messages=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_NEW[0],
            method=Params.UrlsAndMethods.CHAT_NEW[1],
            json_dict={
                'userIds': [Params.ID_START + 3],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object=anything,
            expected_signal_queue_messages=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_NEW[0],
            method=Params.UrlsAndMethods.CHAT_NEW[1],
            json_dict={
                'userIds': [Params.ID_START + 4],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object=anything,
            expected_signal_queue_messages=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_NEW[0],
            method=Params.UrlsAndMethods.CHAT_NEW[1],
            json_dict={
                'userIds': [Params.ID_START + 1],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=409,
        ),
    ]

    message_new = [
        dict(
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 1,
                'text': Params.MESSAGE_TEXTS[0],
            },
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
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
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 'text',
                'text': Params.MESSAGE_TEXTS[0],
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
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 2,
                'text': Params.MESSAGE_TEXTS[0],
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
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 100,
                'text': Params.MESSAGE_TEXTS[0],
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
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 1,
                'text': Params.MESSAGE_TEXTS[0],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object={
                'id': Params.ID_START,
                'chatId': 1,
                'userId': Params.ID_START,
                'text': Params.MESSAGE_TEXTS[0],
                'isRead': False,
                'hasFiles': False,
                'creatingDatetime': anything,
            },
            expected_signal_queue_messages=[
                SignalQueueMessage(
                    user_ids=[Params.ID_START, Params.ID_START + 1],
                    message={
                        'type': 'NEW_MESSAGE',
                        'data': {
                            'messageId': Params.ID_START,
                        },
                    },
                ),
                SignalQueueMessage(
                    user_ids=[Params.ID_START + 1],
                    message={
                        'type': 'NEW_UNREAD_COUNT',
                        'data': {
                            'chatId': 1,
                        },
                    },
                ),
            ],
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 1,
                'text': Params.MESSAGE_TEXTS[1],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object=anything,
            expected_signal_queue_messages=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 1,
                'text': Params.MESSAGE_TEXTS[2],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object=anything,
            expected_signal_queue_messages=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 2,
                'text': Params.MESSAGE_TEXTS[0],
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object=anything,
            expected_signal_queue_messages=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 3,
                'text': Params.MESSAGE_TEXTS[0],
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object=anything,
            expected_signal_queue_messages=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_NEW[0],
            method=Params.UrlsAndMethods.MESSAGE_NEW[1],
            json_dict={
                'chatId': 3,
                'text': Params.BIG_TEXT,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_json_object=anything,
            expected_signal_queue_messages=anything,
        ),
    ]

    message_files_update = [
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[1],
            data={},
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
            url=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[1],
            data=b'',
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[1],
            query_string={
                'messageId': Params.ID_START + 3,
            },
            data={
                'files': deepcopy(Params.FILES),
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
            url=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[1],
            query_string={
                'messageId': 100,
            },
            data={
                'files': deepcopy(Params.FILES),
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=404,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[1],
            query_string={
                'messageId': Params.ID_START + 3,
            },
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
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=413,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_UPDATE[1],
            query_string={
                'messageId': Params.ID_START + 3,
            },
            data={
                'files': deepcopy(Params.FILES),
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=201,
            expected_signal_queue_messages=[
                SignalQueueMessage(
                    user_ids=[Params.ID_START + 1, Params.ID_START + 2],
                    message={
                        'type': 'FILES',
                        'data': {
                            'messageId': Params.ID_START + 3,
                        },
                    },
                ),
            ],
        ),
    ]

    message_read = [
        dict(
            url=Params.UrlsAndMethods.MESSAGE_READ[0],
            method=Params.UrlsAndMethods.MESSAGE_READ[1],
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_READ[0],
            method=Params.UrlsAndMethods.MESSAGE_READ[1],
            json_dict={},
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_READ[0],
            method=Params.UrlsAndMethods.MESSAGE_READ[1],
            json_dict={
                'messageId': Params.ID_START + 3,
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
            url=Params.UrlsAndMethods.MESSAGE_READ[0],
            method=Params.UrlsAndMethods.MESSAGE_READ[1],
            json_dict={
                'messageId': 100,
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
            url=Params.UrlsAndMethods.MESSAGE_READ[0],
            method=Params.UrlsAndMethods.MESSAGE_READ[1],
            json_dict={
                'messageId': Params.ID_START + 1,
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_signal_queue_messages=[
                SignalQueueMessage(
                    user_ids=[Params.ID_START],
                    message={
                        'type': 'READ',
                        'data': {
                            'chatId': 1,
                            'messageIds': [Params.ID_START + 1, Params.ID_START],
                        },
                    },
                ),
                SignalQueueMessage(
                    user_ids=[Params.ID_START + 1],
                    message={
                        'type': 'NEW_UNREAD_COUNT',
                        'data': {
                            'chatId': 1,
                        },
                    },
                ),
            ],
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_READ[0],
            method=Params.UrlsAndMethods.MESSAGE_READ[1],
            json_dict={
                'messageId': Params.ID_START + 1,
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
        ),
    ]

    message_files_names = [
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[1],
            query_string={},
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[1],
            query_string={},
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[1],
            query_string={
                'messageId': 'text',
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
            url=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[1],
            query_string={
                'messageId': Params.ID_START + 3,
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
            url=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[1],
            query_string={
                'messageId': 3333,
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
            url=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_NAMES[1],
            query_string={
                'messageId': Params.ID_START + 3,
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_object=[
                Params.FILES[0][1],
                Params.FILES[1][1],
            ],
        ),
    ]

    message_files_get = [
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_GET[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_GET[1],
            query_string={},
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
            url=Params.UrlsAndMethods.MESSAGE_FILES_GET[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_GET[1],
            query_string={
                'messageId': 'text',
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
            url=Params.UrlsAndMethods.MESSAGE_FILES_GET[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_GET[1],
            query_string={
                'messageId': Params.ID_START + 3,
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
            url=Params.UrlsAndMethods.MESSAGE_FILES_GET[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_GET[1],
            query_string={
                'messageId': Params.ID_START + 3,
                'filename': Params.FILES[0][1],
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
            url=Params.UrlsAndMethods.MESSAGE_FILES_GET[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_GET[1],
            query_string={
                'messageId': Params.ID_START + 3,
                'filename': 'blabla.txt',
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=404,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_GET[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_GET[1],
            query_string={
                'messageId': 13333,
                'filename': 'blabla.txt',
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=404,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_GET[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_GET[1],
            query_string={
                'messageId': Params.ID_START + 3,
                'filename': Params.FILES[0][1],
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_content=Params.FILE_CONTENTS[0],
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE_FILES_GET[0],
            method=Params.UrlsAndMethods.MESSAGE_FILES_GET[1],
            query_string={
                'messageId': Params.ID_START + 3,
                'filename': Params.FILES[1][1],
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_content=Params.FILE_CONTENTS[1],
        ),
    ]

    chat_unread_count = [
        dict(
            url=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[0],
            method=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[1],
            query_string={},
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
            url=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[0],
            method=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[1],
            query_string={},
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[0],
            method=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[1],
            query_string={
                'chatId': 'text',
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
            url=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[0],
            method=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[1],
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
            url=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[0],
            method=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[1],
            query_string={
                'chatId': 100,
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
            url=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[0],
            method=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[1],
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
            expected_json_object={
                'unreadCount': 0,
            },
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[0],
            method=Params.UrlsAndMethods.CHAT_UNREAD_COUNT[1],
            query_string={
                'chatId': 1,
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_object={
                'unreadCount': 1,
            },
        ),
    ]

    chat_typing = [
        dict(
            url=Params.UrlsAndMethods.CHAT_TYPING[0],
            method=Params.UrlsAndMethods.CHAT_TYPING[1],
            json_dict={},
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
            url=Params.UrlsAndMethods.CHAT_TYPING[0],
            method=Params.UrlsAndMethods.CHAT_TYPING[1],
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
            url=Params.UrlsAndMethods.CHAT_TYPING[0],
            method=Params.UrlsAndMethods.CHAT_TYPING[1],
            json_dict={
                'chatId': 'text',
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
            url=Params.UrlsAndMethods.CHAT_TYPING[0],
            method=Params.UrlsAndMethods.CHAT_TYPING[1],
            json_dict={
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
            url=Params.UrlsAndMethods.CHAT_TYPING[0],
            method=Params.UrlsAndMethods.CHAT_TYPING[1],
            json_dict={
                'chatId': 100,
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
            url=Params.UrlsAndMethods.CHAT_TYPING[0],
            method=Params.UrlsAndMethods.CHAT_TYPING[1],
            json_dict={
                'chatId': 1,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_signal_queue_messages=[
                SignalQueueMessage(
                    user_ids=[Params.ID_START + 1],
                    message={
                        'type': 'TYPING',
                        'data': {
                            'chatId': 1,
                            'userId': Params.ID_START,
                        },
                    },
                ),
            ],
        ),
    ]

    chat = [
        dict(
            url=Params.UrlsAndMethods.CHAT[0],
            method=Params.UrlsAndMethods.CHAT[1],
            query_string={},
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT[0],
            method=Params.UrlsAndMethods.CHAT[1],
            query_string={},
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT[0],
            method=Params.UrlsAndMethods.CHAT[1],
            query_string={
                'chatId': 'text',
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
            url=Params.UrlsAndMethods.CHAT[0],
            method=Params.UrlsAndMethods.CHAT[1],
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
            url=Params.UrlsAndMethods.CHAT[0],
            method=Params.UrlsAndMethods.CHAT[1],
            query_string={
                'chatId': 100,
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
            url=Params.UrlsAndMethods.CHAT[0],
            method=Params.UrlsAndMethods.CHAT[1],
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
            expected_json_object={
                'id': 1,
                'isGroup': False,
                'lastMessage': {
                    'id': Params.ID_START + 2,
                    'chatId': 1,
                    'userId': Params.ID_START,
                    'text': Params.MESSAGE_TEXTS[2],
                    'isRead': False,
                    'hasFiles': False,
                    'creatingDatetime': anything,
                },
                'name': None,
                'unreadCount': 0,
                'userIds': [
                    Params.ID_START,
                    Params.ID_START + 1,
                ],
                'interlocutorId': Params.ID_START + 1,
            },
        ),
    ]

    message = [
        dict(
            url=Params.UrlsAndMethods.MESSAGE[0],
            method=Params.UrlsAndMethods.MESSAGE[1],
            query_string={},
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE[0],
            method=Params.UrlsAndMethods.MESSAGE[1],
            query_string={},
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.MESSAGE[0],
            method=Params.UrlsAndMethods.MESSAGE[1],
            query_string={
                'messageId': 'text',
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
            url=Params.UrlsAndMethods.MESSAGE[0],
            method=Params.UrlsAndMethods.MESSAGE[1],
            query_string={
                'messageId': Params.ID_START + 3,
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
            url=Params.UrlsAndMethods.MESSAGE[0],
            method=Params.UrlsAndMethods.MESSAGE[1],
            query_string={
                'messageId': 100,
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
            url=Params.UrlsAndMethods.MESSAGE[0],
            method=Params.UrlsAndMethods.MESSAGE[1],
            query_string={
                'messageId': Params.ID_START + 3,
            },
            cookies={
                'access_token_cookie': Params.SECOND_ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.SECOND_ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_object={
                'id': Params.ID_START + 3,
                'chatId': 2,
                'userId': Params.ID_START + 1,
                'text': Params.MESSAGE_TEXTS[0],
                'isRead': False,
                'hasFiles': True,
                'creatingDatetime': anything,
            },
        ),
    ]

    chat_messages = [
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES[1],
            query_string={},
            cookies={
                'access_token_cookie': create_access_token('what'),
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=401,
            expected_json_object=anything,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES[1],
            query_string={},
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=400,
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES[1],
            query_string={
                'chatId': 'text',
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
            url=Params.UrlsAndMethods.CHAT_MESSAGES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES[1],
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
            url=Params.UrlsAndMethods.CHAT_MESSAGES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES[1],
            query_string={
                'chatId': 100,
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
            url=Params.UrlsAndMethods.CHAT_MESSAGES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES[1],
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
            expected_json_object=[
                {
                    'id': Params.ID_START + 2,
                    'chatId': 1,
                    'userId': Params.ID_START,
                    'text': Params.MESSAGE_TEXTS[2],
                    'isRead': False,
                    'hasFiles': False,
                    'creatingDatetime': anything,
                },
                {
                    'id': Params.ID_START + 1,
                    'chatId': 1,
                    'userId': Params.ID_START,
                    'text': Params.MESSAGE_TEXTS[1],
                    'isRead': True,
                    'hasFiles': False,
                    'creatingDatetime': anything,
                },
                {
                    'id': Params.ID_START,
                    'chatId': 1,
                    'userId': Params.ID_START,
                    'text': Params.MESSAGE_TEXTS[0],
                    'isRead': True,
                    'hasFiles': False,
                    'creatingDatetime': anything,
                },
            ],
        ),
        dict(
            url=Params.UrlsAndMethods.CHAT_MESSAGES[0],
            method=Params.UrlsAndMethods.CHAT_MESSAGES[1],
            query_string={
                'chatId': 1,
                'offset': 1,
            },
            cookies={
                'access_token_cookie': Params.ACCESS_TOKEN,
            },
            headers={
                'X-CSRF-TOKEN': Params.ACCESS_CSRF_TOKEN,
            },

            expected_status_code=200,
            expected_json_object=[
                {
                    'id': Params.ID_START + 1,
                    'chatId': 1,
                    'userId': Params.ID_START,
                    'text': Params.MESSAGE_TEXTS[1],
                    'isRead': True,
                    'hasFiles': False,
                    'creatingDatetime': anything,
                },
                {
                    'id': Params.ID_START,
                    'chatId': 1,
                    'userId': Params.ID_START,
                    'text': Params.MESSAGE_TEXTS[0],
                    'isRead': True,
                    'hasFiles': False,
                    'creatingDatetime': anything,
                },
            ],
        ),
    ]

    user_chats = [
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
            expected_json_object=anything,
        ),
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
            expected_json_object=[
                # sort must be by datetime
                {
                    'id': 3,
                    'isGroup': False,
                    'lastMessage': {
                        'id': Params.ID_START + 5,
                        'chatId': 3,
                        'userId': Params.ID_START,
                        'text': Params.CUT_BIG_TEXT,
                        'isRead': False,
                        'hasFiles': False,
                        'creatingDatetime': anything,
                    },
                    'name': None,
                    'unreadCount': 0,
                    'userIds': [
                        Params.ID_START,
                        Params.ID_START + 3,
                    ],
                    'interlocutorId': Params.ID_START + 3,
                },
                {
                    'id': 1,
                    'isGroup': False,
                    'lastMessage': {
                        'id': Params.ID_START + 2,
                        'chatId': 1,
                        'userId': Params.ID_START,
                        'text': Params.MESSAGE_TEXTS[2],
                        'isRead': False,
                        'hasFiles': False,
                        'creatingDatetime': anything,
                    },
                    'name': None,
                    'unreadCount': 0,
                    'userIds': [
                        Params.ID_START,
                        Params.ID_START + 1,
                    ],
                    'interlocutorId': Params.ID_START + 1,
                },
                {
                    'id': 4,
                    'isGroup': False,
                    'lastMessage': None,
                    'name': None,
                    'unreadCount': 0,
                    'userIds': [
                        Params.ID_START,
                        Params.ID_START + 4,
                    ],
                    'interlocutorId': Params.ID_START + 4,
                },
            ],
        ),
    ]
