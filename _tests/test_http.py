import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from unittest.mock import patch

from config.paths import MEDIA_FOLDER
from db.models import User, Message
from http_.app import app
from http_.users.email.codes.functions import delete_email_code
from http_.common.content_length_check_decorator import _max_lengths
from _tests.common.set_initial_autoincrement_value import set_initial_autoincrement_value
from _tests.common.assert_and_save_jsons_if_failed import assert_and_save_jsons_if_failed
from _tests.common.create_test_db import create_test_db
from _tests.common.values_of_set_cookie_to_dict import values_of_set_cookie_to_dict
from _tests.common.set_for_test_to_values_and_ids import set_for_test_to_values_and_ids
from _tests.common.common_storage import common_storage
from _tests.common.recursive_fill_func_values_of_dict import recursive_fill_func_values_of_dict
from _tests.data.http_.params import Params
from _tests.data.http_.set_for_tests import SetForTest

real_signal_queue_messages = []


def setup_module(module) -> None:
    create_test_db()

    for table_name in (User.__tablename__, Message.__tablename__):
        set_initial_autoincrement_value(table_name, Params.ID_START)

    delete_email_code(Params.EMAIL_FOR_CODE)

    module.max_lengths_patcher = patch.dict(_max_lengths, {
        'user_avatar_edit': len(Params.AVATAR_MAX_BYTES),
        'user_background_edit': len(Params.BACKGROUND_MAX_BYTES),
        'message_files_update': len(Params.FILES_MAX_BYTES),
    })
    module.max_lengths_patcher.start()

    module.send_code_task_delay_patcher = patch('http_.users.email.tasks.send_code_task.delay')
    module.send_code_task_delay_patcher.start()

    def signal_queue_push_mock(self, message):
        real_signal_queue_messages.append(message)

    module.signal_queue_push_patcher = patch('common.signals.queue.SignalQueue.push', signal_queue_push_mock)
    module.signal_queue_push_patcher.start()


def teardown_module(module) -> None:
    module.max_lengths_patcher.stop()
    module.send_code_task_delay_patcher.stop()
    module.signal_queue_push_patcher.stop()


def teardown_function() -> None:
    real_signal_queue_messages.clear()


@pytest.fixture
def test_client() -> FlaskClient:
    return app.test_client()


@pytest.mark.parametrize('kwargs', **set_for_test_to_values_and_ids(SetForTest))
def test_endpoints(test_client: FlaskClient,
                   kwargs,
                   ) -> None:
    kwargs = recursive_fill_func_values_of_dict(kwargs)

    for key, value in kwargs.get('cookies', {}).items():
        test_client.set_cookie(key, value)

    response: TestResponse = test_client.open(
        kwargs['url'],
        method=kwargs['method'],
        query_string=kwargs.get('query_params'),
        headers=kwargs.get('headers'),
        json=kwargs.get('json_dict'),
        data=kwargs.get('data'),
    )
    assert response.status_code == kwargs['expected_status']

    if 'expected_content' in kwargs:
        assert response.data == kwargs['expected_content']
    else:
        assert_and_save_jsons_if_failed(response.json, kwargs.get('expected_json_object'))

    set_cookie_dict = values_of_set_cookie_to_dict(response.headers.getlist('Set-Cookie'))
    assert_and_save_jsons_if_failed(set_cookie_dict, kwargs.get('expected_set_cookie', {}))

    if real_signal_queue_messages:
        assert real_signal_queue_messages == kwargs['expected_signal_queue_messages']

    if 'common_storage_key' in kwargs:
        common_storage[kwargs['common_storage_key']] = {
            'content': response.data,
            'set_cookie': set_cookie_dict,
        }

    if 'expected_existence_of_media_files_or_folders' in kwargs:
        for relative_path in kwargs['expected_existence_of_media_files_or_folders']:
            assert MEDIA_FOLDER.joinpath(relative_path).exists()

    if 'expected_unexistence_of_media_files_or_folders' in kwargs:
        for relative_path in kwargs['expected_unexistence_of_media_files_or_folders']:
            assert not MEDIA_FOLDER.joinpath(relative_path).exists()


@pytest.mark.parametrize('endpoint', Params.Endpoint.list_of_protected_endpoints())
def test_endpoints_for_protect(test_client,
                               endpoint: Params.Endpoint,
                               ) -> None:
    response: TestResponse = test_client.open(
        endpoint[0],
        method=endpoint[1],
    )
    assert response.status_code == 401
