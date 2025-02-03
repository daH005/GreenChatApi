from _tests.common.anything_place import anything
from _tests.data.http_.params import Params

__all__ = (
    'USER_REFRESH_ACCESS',
)

_endpoint = Params.Endpoint.USER_REFRESH_ACCESS
USER_REFRESH_ACCESS = [
    _endpoint.new(
        cookies={
            'refresh_token_cookie': Params.REFRESH_TOKEN,
        },
        headers={
            'X-CSRF-TOKEN': Params.REFRESH_CSRF_TOKEN,
        },
        expected_status=200,
        expected_set_cookie={
            'access_token_cookie': anything,
            'csrf_access_token': anything,
            'refresh_token_cookie': anything,
            'csrf_refresh_token': anything,
        },
    ),
    _endpoint.new(
        cookies={
            'refresh_token_cookie': Params.REFRESH_TOKEN,
        },
        headers={
            'X-CSRF-TOKEN': Params.REFRESH_CSRF_TOKEN,
        },
        expected_status=401,  # check blacklist
        expected_json_object=anything,
    ),
]
