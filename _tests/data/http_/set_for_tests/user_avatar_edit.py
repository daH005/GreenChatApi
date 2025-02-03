from _tests.data.http_.params import Params

__all__ = (
    'USER_AVATAR_EDIT',
)

_endpoint = Params.Endpoint.USER_AVATAR_EDIT
USER_AVATAR_EDIT = [
    _endpoint.new_as_first_user(
        data=b'',
        headers={
            'Content-Type': 'image/png',
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        data=Params.IMAGE_BYTES,
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        data=b'blabla',
        headers={
            'Content-Type': 'image/png',
        },
        expected_status=400,
    ),
    _endpoint.new_as_second_user(
        data=Params.AVATAR_MAX_BYTES * 2,
        expected_status=413,
    ),
    _endpoint.new_as_first_user(
        data=Params.IMAGE_BYTES,
        headers={
            'Content-Type': 'image/png',
        },
        expected_status=200,
    ),
]
