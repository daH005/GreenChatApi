from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'MESSAGE',
)

_endpoint = Params.Endpoint.MESSAGE
MESSAGE = [
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
            'messageId': 100,
        },
        expected_status=404,
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
        },
        expected_status=200,
        expected_json_object={
            'id': Params.ID_START + 3,
            'chatId': 2,
            'userId': Params.ID_START + 1,
            'text': Params.MESSAGE_TEXTS[0],
            'isRead': False,
            'hasFiles': True,
            'creatingDatetime': anything_place,
            'repliedMessage': None,
        },
    ),
]
