from common.signals.message import SignalQueueMessage
from _tests.common.anything_place import anything
from _tests.data.http_.params import Params

__all__ = (
    'CHAT_NEW',
)

_endpoint = Params.Endpoint.CHAT_NEW
CHAT_NEW = [
    _endpoint.new_as_first_user(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'userIds': [],
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'userIds': [Params.ID_START + 1],
        },
        expected_status=201,
        expected_json_object=anything,
        expected_signal_queue_messages=[
            SignalQueueMessage(
                user_ids=[Params.ID_START, Params.ID_START + 1],
                message={
                    'type': 'NEW_CHAT',
                    'data': {
                        'chatId': 1,
                    },
                },
            ),
        ],
    ),
    _endpoint.new_as_second_user(
        json_dict={
            'userIds': [Params.ID_START + 2],
        },
        expected_status=201,
        expected_json_object=anything,
        expected_signal_queue_messages=anything,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'userIds': [Params.ID_START + 3],
        },
        expected_status=201,
        expected_json_object=anything,
        expected_signal_queue_messages=anything,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'userIds': [Params.ID_START + 4],
        },
        expected_status=201,
        expected_json_object=anything,
        expected_signal_queue_messages=anything,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'userIds': [Params.ID_START + 1],
        },
        expected_status=409,
    ),
]
