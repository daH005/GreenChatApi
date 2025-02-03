from _tests.common.anything_place import anything
from _tests.data.http_.params import Params

__all__ = (
    'USER_LOGOUT',
)

_endpoint = Params.Endpoint.USER_LOGOUT
USER_LOGOUT = [
    _endpoint.new_as_first_user(
        expected_status=200,
        expected_set_cookie={
            'access_token_cookie': anything,
            'csrf_access_token': anything,
            'refresh_token_cookie': anything,
            'csrf_refresh_token': anything,
        },
    ),
]
