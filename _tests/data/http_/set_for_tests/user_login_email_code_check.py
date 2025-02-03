from _tests.data.http_.params import Params

__all__ = (
    'USER_LOGIN_EMAIL_CODE_CHECK',
)

_endpoint = Params.Endpoint.USER_LOGIN_EMAIL_CODE_CHECK
USER_LOGIN_EMAIL_CODE_CHECK = [
    _endpoint.new(
        query_params={},
        expected_status=400,
    ),
    _endpoint.new(
        query_params={
            'email': 'a@a',
            'code': Params.EMAIL_CODE,
        },
        expected_status=400,
    ),
    _endpoint.new(
        query_params={
            'email': Params.EMAIL_FOR_CODE,
            'code': 10000,
        },
        expected_status=400,
    ),
    _endpoint.new(
        query_params={
            'email': Params.EMAIL_FOR_CODE,
            'code': 'text',
        },
        expected_status=400,
    ),
    _endpoint.new(
        query_params={
            'email': 'blabla@mail.ru',
            'code': 1001,
        },
        expected_status=200,
        expected_json_object={
            'isThat': False,
        },
    ),
    _endpoint.new(
        query_params={
            'email': Params.EMAIL_FOR_CODE,
            'code': Params.EMAIL_CODE,
        },
        expected_status=200,
        expected_json_object={
            'isThat': True,
        },
    ),
]
