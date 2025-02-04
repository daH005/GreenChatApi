from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'USER_LOGOUT',
)

_endpoint = Params.Endpoint.USER_LOGOUT
USER_LOGOUT = [
    _endpoint.new_as_first_user(
        expected_status=200,
        expected_set_cookie={
            'access_token_cookie': anything_place,
            'csrf_access_token': anything_place,
            'refresh_token_cookie': anything_place,
            'csrf_refresh_token': anything_place,
        },
    ),
    _endpoint.new_as_first_user(
        expected_status=401,  # check for a blacklist
        expected_json_object=anything_place,
    ),
]
