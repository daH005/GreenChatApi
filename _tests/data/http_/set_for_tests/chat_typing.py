from common.signals.message import SignalQueueMessage
from _tests.data.http_.params import Params

__all__ = (
    'CHAT_TYPING',
)

_endpoint = Params.Endpoint.CHAT_TYPING
CHAT_TYPING = [
    _endpoint.new_as_first_user(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 'text',
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 2,
        },
        expected_status=403,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 100,
        },
        expected_status=404,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 1,
        },
        expected_status=200,
        expected_signal_queue_messages=[
            SignalQueueMessage(
                user_ids=[Params.ID_START + 1],
                message={
                    'type': 'TYPING',
                    'data': {
                        'chatId': 1,
                        'userId': Params.ID_START,
                    },
                },
            ),
        ],
    ),
]
