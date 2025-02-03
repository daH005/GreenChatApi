from _tests.data.http_.params import Params

__all__ = (
    'CHAT_UNREAD_COUNT',
)

_endpoint = Params.Endpoint.CHAT_UNREAD_COUNT
CHAT_UNREAD_COUNT = [
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
            'unreadCount': 0,
        },
    ),
    _endpoint.new_as_second_user(
        query_params={
            'chatId': 1,
        },
        expected_status=200,
        expected_json_object={
            'unreadCount': 1,
        },
    ),
]
