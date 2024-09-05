from flask_jwt_extended import create_access_token, create_refresh_token

from api.db.models import User
from api._tests.data.db import USERS
from api._tests.data.json_ import (
    USER_CHATS_KWARGS_AND_JSON_DICTS,
    CHAT_HISTORY_KWARGS_AND_JSON_DICTS,
)

__all__ = (
    'CHECK_EMAIL_TEST_ENDPOINT_KWARGS',
    'LOGIN_TEST_ENDPOINT_KWARGS',
    'REFRESH_ACCESS_TEST_ENDPOINT_KWARGS',
    'USER_INFO_TEST_ENDPOINT_KWARGS',
    'USER_INFO_EDIT_TEST_ENDPOINT_KWARGS',
    'USER_CHATS_TEST_ENDPOINT_KWARGS',
    'CHAT_HISTORY_TEST_ENDPOINT_KWARGS',
)


NEW_USER_EMAIL = 'danil.shevelev.2004@mail.ru'
NEW_USER_ID = USERS[max(USERS.keys())].id + 1

NEW_USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT = {
    'Cookie': 'access_token_cookie=' + create_access_token(NEW_USER_EMAIL) + ';'
              'refresh_token_cookie=' + create_refresh_token(NEW_USER_EMAIL),
}

USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT = {
    'Cookie': 'access_token_cookie=' + create_access_token(USERS[1].email),
}

CHECK_EMAIL_TEST_ENDPOINT_KWARGS = [
    dict(
        data={
            'email': USERS[1].email,
        },
        expected_response_status_code=200,
        expected_response_json_dict={
            'isAlreadyTaken': True,
        },
    ),
    dict(
        data={
            'email': 'isnotalreadytakenemail@mail.ru',
        },
        expected_response_status_code=200,
        expected_response_json_dict={
            'isAlreadyTaken': False,
        },
    ),
    dict(
        expected_response_status_code=400,
        expected_response_json_dict={
            'status': 400,
        },
    ),
]

LOGIN_TEST_ENDPOINT_KWARGS = [
    dict(
        data={
            'code': 9999,
            'email': NEW_USER_EMAIL,
        },
        expected_response_status_code=201,
        expected_response_json_dict={
            'status': 201,
        },
    ),
    dict(
        data={
            'code': 9999,
            'email': NEW_USER_EMAIL,
        },
        expected_response_status_code=200,
        expected_response_json_dict={
            'status': 200,
        },
    ),
    dict(
        data={},
        expected_response_status_code=400,
        expected_response_json_dict={
            'status': 400,
        },
    ),
]

REFRESH_ACCESS_TEST_ENDPOINT_KWARGS = [
    dict(
        headers=NEW_USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        expected_response_status_code=200,
        expected_response_json_dict={
            'status': 200,
        },
    )
]

USER_INFO_TEST_ENDPOINT_KWARGS = [
    dict(
        headers=NEW_USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        expected_response_status_code=200,
        expected_response_json_dict={
            'id': NEW_USER_ID,
            'email': NEW_USER_EMAIL,
            'firstName': User.first_name.default.arg,
            'lastName': User.last_name.default.arg,
        },
    ),
    dict(
        headers=NEW_USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        data={
            'userId': 2,
        },
        expected_response_status_code=200,
        expected_response_json_dict={
            'id': USERS[2].id,
            'firstName': USERS[2].first_name,
            'lastName': USERS[2].last_name,
        },
    ),
    dict(
        headers=NEW_USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        data={
            'userId': 999,
        },
        expected_response_status_code=404,
        expected_response_json_dict={
            'status': 404,
        },
    ),
    dict(
        headers=NEW_USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        data={
            'userId': 'text',
        },
        expected_response_status_code=400,
        expected_response_json_dict={
            'status': 400,
        },
    ),
]

USER_INFO_EDIT_TEST_ENDPOINT_KWARGS = [
    dict(
        headers=NEW_USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        data={
            'firstName': 'newName',
            'lastName': 'newName',
        },
        expected_response_status_code=200,
        expected_response_json_dict={
            'status': 200,
        },
    ),
    dict(
        headers=NEW_USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        data={},
        expected_response_status_code=400,
        expected_response_json_dict={
            'status': 400,
        },
    ),
]

USER_CHATS_TEST_ENDPOINT_KWARGS = [
    dict(
        headers=USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        expected_response_status_code=200,
        expected_response_json_dict=USER_CHATS_KWARGS_AND_JSON_DICTS[0][1],
    ),
    dict(
        headers=NEW_USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        expected_response_status_code=200,
        expected_response_json_dict={
            'chats': [],
        },
    ),
]

CHAT_HISTORY_TEST_ENDPOINT_KWARGS = [
    dict(
        headers=USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        data={
            'chatId': 1,
        },
        expected_response_status_code=200,
        expected_response_json_dict=CHAT_HISTORY_KWARGS_AND_JSON_DICTS[0][1],
    ),
    dict(
        headers=USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        data={
            'chatId': 1,
            'offsetFromEnd': 1,
        },
        expected_response_status_code=200,
        expected_response_json_dict={
            'messages': CHAT_HISTORY_KWARGS_AND_JSON_DICTS[0][1]['messages'][1:]
        },
    ),
    dict(
        headers=USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        data={
            'chatId': 4,
            'offsetFromEnd': 1,
        },
        expected_response_status_code=403,
        expected_response_json_dict={
            'status': 403,
        },
    ),
    dict(
        headers=USER_AUTHORIZATION_HEADERS_WITH_REAL_JWT,
        expected_response_status_code=400,
        expected_response_json_dict={
            'status': 400,
        },
    ),
]
