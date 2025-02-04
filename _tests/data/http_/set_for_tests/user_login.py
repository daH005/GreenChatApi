from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'USER_LOGIN',
)

_endpoint = Params.Endpoint.USER_LOGIN
USER_LOGIN = [
    _endpoint.new(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new(
        json_dict={
            'email': 'a@a',
            'code': Params.EMAIL_CODE,
        },
        expected_status=400,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAIL_FOR_CODE,
            'code': 10000,
        },
        expected_status=400,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAIL_FOR_CODE,
            'code': 'text',
        },
        expected_status=400,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[0],
            'code': Params.EMAIL_CODE,
        },
        expected_status=201,
        expected_set_cookie={
            'access_token_cookie': anything_place,
            'csrf_access_token': anything_place,
            'refresh_token_cookie': anything_place,
            'csrf_refresh_token': anything_place,
        },
        common_storage_key=Params.CommonStorageKey.FIRST_USER_JWT,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[1],
            'code': Params.EMAIL_CODE,
        },
        expected_status=201,
        expected_set_cookie=anything_place,
        common_storage_key=Params.CommonStorageKey.SECOND_USER_JWT,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[2],
            'code': Params.EMAIL_CODE,
        },
        expected_status=201,
        expected_set_cookie=anything_place,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[3],
            'code': Params.EMAIL_CODE,
        },
        expected_status=201,
        expected_set_cookie=anything_place,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[4],
            'code': Params.EMAIL_CODE,
        },
        expected_status=201,
        expected_set_cookie=anything_place,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[0],
            'code': Params.EMAIL_CODE,
        },
        expected_status=200,
        expected_set_cookie={
            'access_token_cookie': anything_place,
            'csrf_access_token': anything_place,
            'refresh_token_cookie': anything_place,
            'csrf_refresh_token': anything_place,
        },
    ),
]
