from _tests.data.http_.params import Params

__all__ = (
    'USER',
)

_endpoint = Params.Endpoint.USER
USER = [
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
        expected_status=200,
        expected_json_object={
            'id': Params.ID_START,
            'email': Params.EMAILS[0],
            'firstName': Params.NEW_FIRST_NAME,
            'lastName': Params.NEW_LAST_NAME,
            'isOnline': False,
        },
    ),
    _endpoint.new_as_first_user(
        query_params={
            'userId': Params.ID_START + 1,
        },
        expected_status=200,
        expected_json_object={
            'id': Params.ID_START + 1,
            'firstName': Params.DEFAULT_FIRST_NAME,
            'lastName': Params.DEFAULT_LAST_NAME,
            'isOnline': False,
        },
    ),
]
