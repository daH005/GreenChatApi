from copy import deepcopy
from io import BytesIO

from common.signals.message import SignalQueueMessage
from _tests.common.anything_place import anything_place
from _tests.data.http_.params import Params

__all__ = (
    'MESSAGE_FILES_UPDATE',
)

_endpoint = Params.Endpoint.MESSAGE_FILES_UPDATE
MESSAGE_FILES_UPDATE = [
    _endpoint.new_as_first_user(
        data=b'',
        expected_status=400,
    ),
    _endpoint.new_as_first_user(
        query_params={
            'messageId': Params.ID_START + 3,
        },
        data={
            'files': deepcopy(Params.FILES),
        },
        expected_status=403,
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': 100,
        },
        data={
            'files': deepcopy(Params.FILES),
        },
        expected_status=404,
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
        },
        data={
            'files': [
                (
                    BytesIO(Params.FILES_MAX_BYTES[:len(Params.FILES_MAX_BYTES) // 4]),
                    'large1.txt',
                ),
                (
                    BytesIO(Params.FILES_MAX_BYTES),
                    'large2.txt',
                ),
            ],
        },
        expected_status=413,
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
        },
        data={
            'files': [deepcopy(Params.FILES[0])],
        },
        expected_status=201,
        expected_signal_queue_messages=[
            SignalQueueMessage(
                user_ids=[Params.ID_START + 1, Params.ID_START + 2],
                message={
                    'type': 'FILES',
                    'data': {
                        'messageId': Params.ID_START + 3,
                    },
                },
            ),
        ],
        expected_existence_of_media_files_or_folders=[f'./files/{Params.ID_START + 3}/ZmlsZTEudHh0'],
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
        },
        data={
            'files': [deepcopy(Params.FILES[1])],
        },
        expected_status=201,
        expected_signal_queue_messages=anything_place,
        expected_existence_of_media_files_or_folders=[f'./files/{Params.ID_START + 3}/ZmlsZTIucHk='],
    ),
    _endpoint.new_as_second_user(
        query_params={
            'messageId': Params.ID_START + 3,
        },
        data={
            'files': [deepcopy(Params.FILE_TO_CREATE_AND_DELETE)],
        },
        expected_status=201,
        expected_signal_queue_messages=anything_place,
        expected_existence_of_media_files_or_folders=[f'./files/{Params.ID_START + 3}/ZmlsZUQuanM='],
    ),
]
