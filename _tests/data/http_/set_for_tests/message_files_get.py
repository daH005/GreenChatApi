from _tests.data.http_.params import Params

__all__ = (
    'MESSAGE_FILES_GET',
)

_endpoint = Params.Endpoint.MESSAGE_FILES_GET
MESSAGE_FILES_GET = [
    _endpoint.new_as_second_user(
        query_params={
            'messageId': 'text',
            'filename': Params.FILES[0][1],
        },
        expected_status=400,
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'messageId': Params.ID_START + 3,
            'filename': Params.FILES[0][1],
        },
        expected_status=403,
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
            'filename': 'blabla.txt',
        },
        expected_status=404,
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': 13333,
            'filename': 'blabla.txt',
        },
        expected_status=404,
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
            'filename': Params.FILES[0][1],
        },
        expected_status=200,
        expected_content=Params.FILE_CONTENTS[0],
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
            'filename': Params.FILES[1][1],
        },
        expected_status=200,
        expected_content=Params.FILE_CONTENTS[1],
    ),
]
