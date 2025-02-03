from _tests.common.anything_place import anything
from _tests.data.http_.params import Params

__all__ = (
    'USER_CHATS',
)

_endpoint = Params.Endpoint.USER_CHATS
USER_CHATS = [
    _endpoint.new_as_first_user(
        expected_status=200,
        expected_json_object=[
            # sort must be by datetime
            {
                'id': 3,
                'isGroup': False,
                'lastMessage': {
                    'id': Params.ID_START + 5,
                    'chatId': 3,
                    'userId': Params.ID_START,
                    'text': Params.CUT_BIG_TEXT,
                    'isRead': False,
                    'hasFiles': False,
                    'creatingDatetime': anything,
                    'repliedMessage': None,
                },
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
                'lastMessage': {
                    'id': Params.ID_START + 2,
                    'chatId': 1,
                    'userId': Params.ID_START,
                    'text': Params.UPDATED_TEXT,
                    'isRead': False,
                    'hasFiles': False,
                    'creatingDatetime': anything,
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
            {
                'id': 4,
                'isGroup': False,
                'lastMessage': None,
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
]
