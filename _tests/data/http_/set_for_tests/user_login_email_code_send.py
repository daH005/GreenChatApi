from _tests.data.http_.params import Params

__all__ = (
    'USER_LOGIN_EMAIL_CODE_SEND',
)

_endpoint = Params.Endpoint.USER_LOGIN_EMAIL_CODE_SEND
USER_LOGIN_EMAIL_CODE_SEND = [
    _endpoint.new(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new(
        json_dict={
            'email': 'a@a',
        },
        expected_status=400,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAIL_FOR_CODE,
        },
        expected_status=202,
    ),
    _endpoint.new(
        json_dict={
            'email': Params.EMAIL_FOR_CODE,
        },
        expected_status=409,
    ),
]
