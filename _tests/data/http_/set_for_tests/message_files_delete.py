from common.signals.message import SignalQueueMessage
from _tests.data.http_.params import Params

__all__ = (
    'MESSAGE_FILES_DELETE',
)

_endpoint = Params.Endpoint.MESSAGE_FILES_DELETE
MESSAGE_FILES_DELETE = [
    _endpoint.new_as_first_user(
        json_dict={},
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'filenames': 1,
        },
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        json_dict={
            'messageId': Params.ID_START + 3,
            'filenames': [Params.FILE_TO_CREATE_AND_DELETE[1]],
        },
        expected_status=403,
    ),
    _endpoint.new_as_second_user(
        json_dict={
            'messageId': 100,
            'filenames': [Params.FILE_TO_CREATE_AND_DELETE[1]],
        },
        expected_status=404,
    ),
    _endpoint.new_as_second_user(
        json_dict={
            'messageId': Params.ID_START + 3,
            'filenames': [Params.FILE_TO_CREATE_AND_DELETE[1]],
        },
        expected_status=200,
        expected_signal_queue_messages=[
            SignalQueueMessage(
                user_ids=[Params.ID_START + 1, Params.ID_START + 2],
                message={
                    'type': 'FILES',
                    'data': {
                        'chatId': 2,
                        'messageId': Params.ID_START + 3,
                    },
                },
            ),
        ],
        expected_unexistence_of_media_files_or_folders=[f'./files/{Params.ID_START + 3}/ZmlsZUQuanM='],
    ),
]
