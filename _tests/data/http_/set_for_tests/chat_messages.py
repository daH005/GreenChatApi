from _tests.common.anything_place import anything
from _tests.data.http_.params import Params

__all__ = (
    'CHAT_MESSAGES',
)

_endpoint = Params.Endpoint.CHAT_MESSAGES
CHAT_MESSAGES = [
    _endpoint.new_as_first_user(
        query_params={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'chatId': 'text',
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'chatId': 2,
        },
        expected_status=403,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'chatId': 100,
        },
        expected_status=404,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'chatId': 1,
        },
        expected_status=200,
        expected_json_object=[
            {
                'id': Params.ID_START + 2,
                'chatId': 1,
                'userId': Params.ID_START,
                'text': Params.UPDATED_TEXT,
                'isRead': False,
                'hasFiles': False,
                'creatingDatetime': anything,
                'repliedMessage': None,
            },
            {
                'id': Params.ID_START + 1,
                'chatId': 1,
                'userId': Params.ID_START,
                'text': Params.MESSAGE_TEXTS[1],
                'isRead': True,
                'hasFiles': False,
                'creatingDatetime': anything,
                'repliedMessage': {
                    'id': Params.ID_START + 2,
                    'userId': Params.ID_START,
                    'text': Params.UPDATED_TEXT,
                },
            },
            {
                'id': Params.ID_START,
                'chatId': 1,
                'userId': Params.ID_START,
                'text': Params.MESSAGE_TEXTS[0],
                'isRead': True,
                'hasFiles': False,
                'creatingDatetime': anything,
                'repliedMessage': None,
            },
        ],
    ),
    _endpoint.new_as_first_user(
        query_params={
            'chatId': 1,
            'offset': 1,
        },
        expected_status=200,
        expected_json_object=[
            {
                'id': Params.ID_START + 1,
                'chatId': 1,
                'userId': Params.ID_START,
                'text': Params.MESSAGE_TEXTS[1],
                'isRead': True,
                'hasFiles': False,
                'creatingDatetime': anything,
                'repliedMessage': anything,
            },
            {
                'id': Params.ID_START,
                'chatId': 1,
                'userId': Params.ID_START,
                'text': Params.MESSAGE_TEXTS[0],
                'isRead': True,
                'hasFiles': False,
                'creatingDatetime': anything,
                'repliedMessage': None,
            },
        ],
    ),
]
