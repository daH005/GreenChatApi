from common.signals.message import SignalQueueMessage
from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'MESSAGE_NEW',
)

_endpoint = Params.Endpoint.MESSAGE_NEW
MESSAGE_NEW = [
    _endpoint.new_as_first_user(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 'text',
            'text': Params.MESSAGE_TEXTS[0],
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 2,
            'text': Params.MESSAGE_TEXTS[0],
        },
        expected_status=403,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 100,
            'text': Params.MESSAGE_TEXTS[0],
        },
        expected_status=404,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 1,
            'repliedMessageId': 999,
            'text': Params.MESSAGE_TEXTS[1],
        },
        expected_status=404,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 1,
            'text': Params.MESSAGE_TEXTS[0],
        },
        expected_status=201,
        expected_json_object={
            'id': Params.ID_START,
            'chatId': 1,
            'userId': Params.ID_START,
            'text': Params.MESSAGE_TEXTS[0],
            'isRead': False,
            'hasFiles': False,
            'creatingDatetime': anything_place,
            'repliedMessage': None,
        },
        expected_signal_queue_messages=[
            SignalQueueMessage(
                user_ids=[Params.ID_START, Params.ID_START + 1],
                message={
                    'type': 'NEW_MESSAGE',
                    'data': {
                        'chatId': 1,
                        'messageId': Params.ID_START,
                    },
                },
            ),
        ],
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 2,
            'repliedMessageId': Params.ID_START,
            'text': Params.MESSAGE_TEXTS[1],
        },
        expected_status=403,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 1,
            'repliedMessageId': Params.ID_START,
            'text': Params.MESSAGE_TEXTS[1],
        },
        expected_status=201,
        expected_json_object=anything_place,
        expected_signal_queue_messages=anything_place,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 1,
            'text': Params.MESSAGE_TEXTS[2],
        },
        expected_status=201,
        expected_json_object=anything_place,
        expected_signal_queue_messages=anything_place,
    ),
    _endpoint.new_as_second_user(
        json_dict={
            'chatId': 2,
            'text': Params.MESSAGE_TEXTS[0],
        },
        expected_status=201,
        expected_json_object=anything_place,
        expected_signal_queue_messages=anything_place,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 3,
            'text': Params.MESSAGE_TEXTS[0],
        },
        expected_status=201,
        expected_json_object=anything_place,
        expected_signal_queue_messages=anything_place,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 3,
            'text': Params.BIG_TEXT,
        },
        expected_status=201,
        expected_json_object=anything_place,
        expected_signal_queue_messages=anything_place,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'chatId': 3,
            'text': '---',
        },
        expected_status=201,
        expected_json_object=anything_place,
        expected_signal_queue_messages=anything_place,
    ),
]
