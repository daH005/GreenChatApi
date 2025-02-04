from io import BytesIO
from enum import Enum
from typing import Self

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_csrf_token,
)

from config import EMAIL_PASS_CODE
from db.models import User

__all__ = (
    'Params',
)


class Params:

    class Endpoint(tuple[str, str], Enum):

        USER_LOGIN = '/user/login', 'POST'
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
        MESSAGE_DELETE = '/message/delete', 'DELETE'
        MESSAGE_EDIT = '/message/edit', 'PUT'
        MESSAGE_FILES_UPDATE = '/message/files/update', 'PUT'
        MESSAGE_FILES_DELETE = '/message/files/delete', 'DELETE'
        MESSAGE_READ = '/message/read', 'PUT'
        MESSAGE_FILES_NAMES = '/message/files/names', 'GET'
        MESSAGE_FILES_GET = '/message/files/get', 'GET'
        CHAT_UNREAD_COUNT = '/chat/unreadCount', 'GET'
        CHAT_TYPING = '/chat/typing', 'POST'
        CHAT = '/chat', 'GET'
        MESSAGE = '/message', 'GET'
        CHAT_MESSAGES = '/chat/messages', 'GET'

        USER_CHATS = '/user/chats', 'GET'

        @classmethod
        def list_of_protected_endpoints(cls) -> list[Self]:
            protected_endpoints = [
                cls.USER_LOGIN,
                cls.USER_LOGIN_EMAIL_CODE_CHECK,
                cls.USER_LOGIN_EMAIL_CODE_SEND,
            ]
            return list(filter(lambda x: x not in protected_endpoints, list(cls)))

        def new_as_first_user(self, **kwargs):
            return self.new_as_some_user(
                Params.ACCESS_TOKEN,
                Params.ACCESS_CSRF_TOKEN,
                **kwargs,
            )

        def new_as_second_user(self, **kwargs):
            return self.new_as_some_user(
                Params.SECOND_ACCESS_TOKEN,
                Params.SECOND_ACCESS_CSRF_TOKEN,
                **kwargs,
            )

        def new_as_some_user(self, token: str,
                             csrf_token: str,
                             **kwargs,
                             ):
            if self[1] != 'GET':
                csrf_headers = {
                    'X-CSRF-TOKEN': csrf_token,
                }
            else:
                csrf_headers = {}

            return self.new(
                cookies={
                    'access_token_cookie': token,
                    **kwargs.pop('cookies', {}),
                },
                headers={
                    **csrf_headers,
                    **kwargs.pop('headers', {}),
                },
                **kwargs,
            )

        def new(self, **kwargs):
            return dict(
                url=self[0],
                method=self[1],
                **kwargs,
            )

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

    FILE_TO_CREATE_AND_DELETE = (
        BytesIO(b'file'),
        'fileD.js',
    )

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

    ACCESS_TOKEN = create_access_token(ID_START)
    ACCESS_CSRF_TOKEN = get_csrf_token(ACCESS_TOKEN)

    REFRESH_TOKEN = create_refresh_token(ID_START)
    REFRESH_CSRF_TOKEN = get_csrf_token(REFRESH_TOKEN)

    SECOND_ACCESS_TOKEN = create_access_token(ID_START + 1)
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

    UPDATED_TEXT = 'newtext'
