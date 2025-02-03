from _tests.data.http_.params import Params

__all__ = (
    'MESSAGE_FILES_NAMES',
)

_endpoint = Params.Endpoint.MESSAGE_FILES_NAMES
MESSAGE_FILES_NAMES = [
    _endpoint.new_as_first_user(
        query_params={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'messageId': 'text',
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'messageId': Params.ID_START + 3,
        },
        expected_status=403,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'messageId': 3333,
        },
        expected_status=404,
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
        },
        expected_status=200,
        expected_json_object=[
            Params.FILES[0][1],
            Params.FILES[1][1],
        ],
    ),
]
