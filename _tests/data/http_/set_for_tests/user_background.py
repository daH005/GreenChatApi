from http_.users.backgrounds.blueprint import _DEFAULT_BACKGROUND_PATH
from _tests.data.http_.params import Params

__all__ = (
    'USER_BACKGROUND',
)

_endpoint = Params.Endpoint.USER_BACKGROUND
USER_BACKGROUND = [
    _endpoint.new_as_first_user(
        expected_status=200,
        expected_content=Params.IMAGE_BYTES,
    ),
    _endpoint.new_as_second_user(
        expected_status=200,
        expected_content=_DEFAULT_BACKGROUND_PATH.read_bytes(),
    ),
]
