from common.signals.message import SignalQueueMessage
from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'MESSAGE_EDIT',
)

_endpoint = Params.Endpoint.MESSAGE_EDIT
MESSAGE_EDIT = [
    _endpoint.new_as_first_user(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': 'text',
            'text': Params.UPDATED_TEXT,
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': Params.ID_START + 3,
            'text': Params.UPDATED_TEXT,
        },
        expected_status=403,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': Params.ID_START + 2,
            'repliedMessageId': Params.ID_START + 3,
            'text': Params.UPDATED_TEXT,
        },
        expected_status=403,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': 100,
            'text': Params.UPDATED_TEXT,
        },
        expected_status=404,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': Params.ID_START + 2,
            'repliedMessageId': 999,
            'text': Params.UPDATED_TEXT,
        },
        expected_status=404,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': Params.ID_START,
            'repliedMessageId': Params.ID_START,
        },
        expected_status=409,
        expected_signal_queue_messages=anything_place,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': Params.ID_START + 2,
            'text': Params.UPDATED_TEXT,
        },
        expected_status=200,
        expected_signal_queue_messages=[
            SignalQueueMessage(
                user_ids=[Params.ID_START, Params.ID_START + 1],
                message={
                    'type': 'MESSAGE_EDIT',
                    'data': {
                        'chatId': 1,
                        'messageId': Params.ID_START + 2,
                    },
                },
            ),
        ],
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': Params.ID_START + 1,
            'repliedMessageId': Params.ID_START + 2,
        },
        expected_status=200,
        expected_signal_queue_messages=anything_place,
    ),
]
