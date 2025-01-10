import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from unittest.mock import patch

from http_.app import app
from http_.email.codes.functions import delete_email_code, make_and_save_email_code
from http_.common.content_length_check_decorator import _max_lengths
from db.models import ChatMessageStorage
from _tests.common.set_initial_autoincrement_value import set_initial_autoincrement_value
from _tests.common.assert_and_save_jsons_if_failed import assert_and_save_jsons_if_failed
from _tests.common.create_test_db import create_test_db
from _tests.common.values_of_set_cookie_to_dict import values_of_set_cookie_to_dict
from _tests.common.set_for_test_to_values_and_ids import set_for_test_to_values_and_ids
from _tests.data.http_ import Params, ORMObjects, SetForTest


def setup_module(module) -> None:
    create_test_db(ORMObjects.all)
    set_initial_autoincrement_value(ChatMessageStorage.__tablename__, Params.STORAGE_ID)

    delete_email_code(Params.user['_email'])
    delete_email_code(Params.EMAIL_WITH_CODE)
    make_and_save_email_code(Params.EMAIL_WITH_CODE, Params.EMAIL_CODE)

    def chat_message_storage_init_mock(self):
        module.chat_message_storage_init_patcher.temp_original(
            self, _chat_message_id=Params.CHAT_MESSAGE_ID_WITH_STORAGE,
        )

    module.chat_message_storage_init_patcher = patch('db.models.ChatMessageStorage.__init__',
                                                     chat_message_storage_init_mock)
    module.chat_message_storage_init_patcher.start()

    module.max_lengths_patcher = patch.dict(_max_lengths, {
        'user_avatar_edit': len(Params.AVATAR_MAX_BYTES),
        'user_background_edit': len(Params.BACKGROUND_MAX_BYTES),
        'chat_messages_files_save': len(Params.FILES_MAX_BYTES),
    })
    module.max_lengths_patcher.start()

    module.send_code_task_delay_patcher = patch('http_.email.tasks.send_code_task.delay')
    module.send_code_task_delay_patcher.start()


def teardown_module(module) -> None:
    module.chat_message_storage_init_patcher.stop()
    module.max_lengths_patcher.stop()
    module.send_code_task_delay_patcher.stop()


@pytest.fixture
def test_client() -> FlaskClient:
    return app.test_client()


@pytest.mark.parametrize('kwargs', **set_for_test_to_values_and_ids(SetForTest))
def test_endpoints(test_client: FlaskClient, kwargs) -> None:
    for key, value in kwargs.get('cookies', {}).items():
        test_client.set_cookie(key, value)

    response: TestResponse = test_client.open(
        kwargs['url'],
        method=kwargs['method'],
        query_string=kwargs.get('query_string'),
        headers=kwargs.get('headers'),
        json=kwargs.get('json_dict'),
        data=kwargs.get('data'),
    )

    assert response.status_code == kwargs['expected_status_code']

    if 'expected_content' in kwargs:
        assert response.data == kwargs['expected_content']
    else:
        assert_and_save_jsons_if_failed(response.json, kwargs.get('expected_json_dict'))

    values_of_set_cookie = response.headers.getlist('Set-Cookie')
    assert_and_save_jsons_if_failed(values_of_set_cookie_to_dict(values_of_set_cookie), kwargs.get('expected_set_cookie', {}))
