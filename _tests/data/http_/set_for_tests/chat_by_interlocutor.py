from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'CHAT_BY_INTERLOCUTOR',
)

_endpoint = Params.Endpoint.CHAT_BY_INTERLOCUTOR
CHAT_BY_INTERLOCUTOR = [
    _endpoint.new_as_first_user(
        query_params={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'interlocutorId': 'text',
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'interlocutorId': Params.ID_START + 2,
        },
        expected_status=404,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'interlocutorId': 100,
        },
        expected_status=404,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'interlocutorId': Params.ID_START + 1,
        },
        expected_status=200,
        expected_json_object={
            'id': 1,
            'isGroup': False,
            'lastMessage': {
                'id': Params.ID_START + 2,
                'chatId': 1,
                'userId': Params.ID_START,
                'text': Params.UPDATED_TEXT,
                'isRead': False,
                'hasFiles': False,
                'creatingDatetime': anything_place,
                'repliedMessage': None,
            },
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
