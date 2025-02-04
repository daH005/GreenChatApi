from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'USER_REFRESH_ACCESS',
)

_endpoint = Params.Endpoint.USER_REFRESH_ACCESS
USER_REFRESH_ACCESS = [
    _endpoint.new_as_first_user(
        jwt_kind='refresh',
        expected_status=200,
        expected_set_cookie={
            'access_token_cookie': anything_place,
            'csrf_access_token': anything_place,
            'refresh_token_cookie': anything_place,
            'csrf_refresh_token': anything_place,
        },
    ),
    _endpoint.new_as_first_user(
        jwt_kind='refresh',
        expected_status=401,  # check for a blacklist
        expected_json_object=anything_place,
    ),
]
