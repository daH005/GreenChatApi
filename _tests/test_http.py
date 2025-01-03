import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from unittest.mock import patch

from http_.app import app
from http_.email.codes.functions import delete_email_code, make_and_save_email_code
from http_.files.functions import STORAGE_ID_PATH
from _tests.common.assert_and_save_jsons_if_failed import assert_and_save_jsons_if_failed
from _tests.common.create_test_db import create_test_db
from _tests.common.values_of_set_cookie_to_dict import values_of_set_cookie_to_dict
from _tests.data.http_ import Params, ORMObjects, SetForTest

_teardown_appcontext_funcs_backup = app.teardown_appcontext_funcs.copy()


def setup_module() -> None:
    create_test_db(ORMObjects.all)

    delete_email_code(Params.user['_email'])
    delete_email_code(Params.EMAIL_WITH_CODE)
    make_and_save_email_code(Params.EMAIL_WITH_CODE, Params.EMAIL_CODE)

    STORAGE_ID_PATH.write_text(str(Params.STORAGE_ID))

    patch('http_.email.tasks.send_code_task').start()
    app.teardown_appcontext_funcs.clear()


def teardown_module() -> None:
    patch('db.builder.db_builder.session.remove').stop()
    patch('http_.email.tasks.send_code_task').stop()
    app.teardown_appcontext_funcs.extend(_teardown_appcontext_funcs_backup)


@pytest.fixture
def test_client() -> FlaskClient:
    return app.test_client()


@pytest.mark.parametrize('kwargs', SetForTest.all)
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
