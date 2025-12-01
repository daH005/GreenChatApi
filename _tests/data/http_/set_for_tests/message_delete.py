from common.signals.message import SignalQueueMessage
from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'MESSAGE_DELETE',
)

_endpoint = Params.Endpoint.MESSAGE_DELETE
MESSAGE_DELETE = [
    _endpoint.new_as_first_user(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': 'text',
        },
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
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': Params.ID_START + 6,
        },
        expected_status=200,
        expected_signal_queue_messages=[
            SignalQueueMessage(
                user_ids=[Params.ID_START, Params.ID_START + 3],
                message={
                    'type': 'MESSAGE_DELETE',
                    'data': {
                        'messageId': Params.ID_START + 6,
                    },
                },
            ),
        ],
    ),
    _endpoint.new_as_second_user(
        json_dict={
            'messageId': Params.ID_START + 3,
        },
        expected_status=200,
        expected_signal_queue_messages=anything_place,
        expected_unexistence_of_media_files_or_folders=[f'./files/{Params.ID_START + 3}'],
    ),
]
