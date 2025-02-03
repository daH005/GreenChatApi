from common.signals.message import SignalQueueMessage
from _tests.data.http_.params import Params

__all__ = (
    'MESSAGE_READ',
)

_endpoint = Params.Endpoint.MESSAGE_READ
MESSAGE_READ = [
    _endpoint.new_as_first_user(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': Params.ID_START + 3,
        },
        expected_status=403,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': 100,
        },
        expected_status=404,
    ),
    _endpoint.new_as_second_user(
        json_dict={
            'messageId': Params.ID_START + 1,
        },
        expected_status=200,
        expected_signal_queue_messages=[
            SignalQueueMessage(
                user_ids=[Params.ID_START],
                message={
                    'type': 'READ',
                    'data': {
                        'chatId': 1,
                        'messageIds': [Params.ID_START + 1, Params.ID_START],
                    },
                },
            ),
            SignalQueueMessage(
                user_ids=[Params.ID_START + 1],
                message={
                    'type': 'NEW_UNREAD_COUNT',
                    'data': {
                        'chatId': 1,
                    },
                },
            ),
        ],
    ),
    _endpoint.new_as_second_user(
        json_dict={
            'messageId': Params.ID_START + 1,
        },
        expected_status=200,
    ),
]
