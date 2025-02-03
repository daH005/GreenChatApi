from _tests.common.anything_place import anything
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
            'access_token_cookie': anything,
            'csrf_access_token': anything,
            'refresh_token_cookie': anything,
            'csrf_refresh_token': anything,
        },
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[1],
            'code': Params.EMAIL_CODE,
        },
        expected_status=201,
        expected_set_cookie=anything,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[2],
            'code': Params.EMAIL_CODE,
        },
        expected_status=201,
        expected_set_cookie=anything,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[3],
            'code': Params.EMAIL_CODE,
        },
        expected_status=201,
        expected_set_cookie=anything,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[4],
            'code': Params.EMAIL_CODE,
        },
        expected_status=201,
        expected_set_cookie=anything,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAILS[0],
            'code': Params.EMAIL_CODE,
        },
        expected_status=200,
        expected_set_cookie={
            'access_token_cookie': anything,
            'csrf_access_token': anything,
            'refresh_token_cookie': anything,
            'csrf_refresh_token': anything,
        },
    ),
]
