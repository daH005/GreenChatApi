from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'CHAT',
)

_endpoint = Params.Endpoint.CHAT
CHAT = [
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
        expected_json_object={
            'id': 1,
            'isGroup': False,
            'name': None,
            'unreadCount': 0,
            'userIds': [
                Params.ID_START,
                Params.ID_START + 1,
            ],
            'interlocutorId': Params.ID_START + 1,
        },
    ),
]
