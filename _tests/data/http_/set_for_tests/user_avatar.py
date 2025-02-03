from http_.users.avatars.blueprint import _DEFAULT_AVATAR_PATH
from _tests.data.http_.params import Params

__all__ = (
    'USER_AVATAR',
)

_endpoint = Params.Endpoint.USER_AVATAR
USER_AVATAR = [
    _endpoint.new_as_first_user(
        query_params={
            'userId': 'text',
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'userId': 1333,
        },
        expected_status=404,
    ),
    _endpoint.new_as_first_user(
        query_params={},
        expected_status=200,
        expected_content=Params.IMAGE_BYTES,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'userId': Params.ID_START + 1,
        },
        expected_status=200,
        expected_content=_DEFAULT_AVATAR_PATH.read_bytes(),
    ),
]
