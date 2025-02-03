from _tests.data.http_.params import Params

__all__ = (
    'USER_EDIT',
)

_endpoint = Params.Endpoint.USER_EDIT
USER_EDIT = [
    _endpoint.new_as_first_user(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'firstName': '',
            'lastName': ''
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'firstName': Params.NEW_FIRST_NAME,
            'lastName': Params.NEW_LAST_NAME,
        },
        expected_status=200,
    ),
]
