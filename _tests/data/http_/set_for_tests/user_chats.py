from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'USER_CHATS',
)

_endpoint = Params.Endpoint.USER_CHATS
USER_CHATS = [
    _endpoint.new_as_first_user(
        expected_status=200,
        expected_json_object=[
            # sort must be by datetime of last messages
            {
                'id': 3,
                'isGroup': False,
                'name': None,
                'unreadCount': 0,
                'userIds': [
                    Params.ID_START,
                    Params.ID_START + 3,
                ],
                'interlocutorId': Params.ID_START + 3,
            },
            {
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
            {
                'id': 4,
                'isGroup': False,
                'name': None,
                'unreadCount': 0,
                'userIds': [
                    Params.ID_START,
                    Params.ID_START + 4,
                ],
                'interlocutorId': Params.ID_START + 4,
            },
        ],
    ),
    _endpoint.new_as_first_user(
        query_params={
            'offset': 1,
            'size': 1,
        },
        expected_status=200,
        expected_json_object=[
            {
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
        ],
    ),
]
