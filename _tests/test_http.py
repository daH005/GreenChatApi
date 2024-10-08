import pytest
from http import HTTPStatus
from werkzeug.test import TestResponse
from unittest.mock import patch

from http_.app import app
from _tests.common_ import JsonDictType, HeadersOrQueryArgsType
from _tests.data.http_ import (
    CHECK_EMAIL_TEST_ENDPOINT_KWARGS,
    LOGIN_TEST_ENDPOINT_KWARGS,
    REFRESH_ACCESS_TEST_ENDPOINT_KWARGS,
    USER_INFO_TEST_ENDPOINT_KWARGS,
    USER_INFO_EDIT_TEST_ENDPOINT_KWARGS,
    USER_CHATS_TEST_ENDPOINT_KWARGS,
    CHAT_HISTORY_TEST_ENDPOINT_KWARGS,
)

# `use_cookies` обязательно нужно оставить в False, поскольку мы сами управляем куками и меняем их в ходе тестов.
_test_client = app.test_client(use_cookies=False)


def setup_module() -> None:
    patch('http_.email.tasks.send_code_task').start()
    app.teardown_appcontext_funcs.clear()


@pytest.mark.parametrize('test_endpoint_kwargs', CHECK_EMAIL_TEST_ENDPOINT_KWARGS)
def test_check_email(test_endpoint_kwargs: dict) -> None:
    _test_get_endpoint(urn='/user/login/email/check', **test_endpoint_kwargs)


@pytest.mark.parametrize('test_endpoint_kwargs', LOGIN_TEST_ENDPOINT_KWARGS)
def test_login(test_endpoint_kwargs: dict) -> None:
    _test_post_or_put_endpoint(urn='/user/login', method='POST', **test_endpoint_kwargs)


@pytest.mark.parametrize('test_endpoint_kwargs', REFRESH_ACCESS_TEST_ENDPOINT_KWARGS)
def test_refresh_access(test_endpoint_kwargs: dict) -> None:
    _test_post_or_put_endpoint(urn='/user/refreshAccess', method='POST', **test_endpoint_kwargs)


@pytest.mark.parametrize('test_endpoint_kwargs', USER_INFO_TEST_ENDPOINT_KWARGS)
def test_user_info(test_endpoint_kwargs: dict) -> None:
    _test_get_endpoint(urn='/user/info', **test_endpoint_kwargs)


@pytest.mark.parametrize('test_endpoint_kwargs', USER_INFO_EDIT_TEST_ENDPOINT_KWARGS)
def test_user_info_edit(test_endpoint_kwargs: dict) -> None:
    _test_post_or_put_endpoint(urn='/user/info/edit', method='PUT', **test_endpoint_kwargs)


@pytest.mark.parametrize('test_endpoint_kwargs', USER_CHATS_TEST_ENDPOINT_KWARGS)
def test_user_chats(test_endpoint_kwargs: dict) -> None:
    _test_get_endpoint(urn='/user/chats', **test_endpoint_kwargs)


@pytest.mark.parametrize('test_endpoint_kwargs', CHAT_HISTORY_TEST_ENDPOINT_KWARGS)
def test_chat_history(test_endpoint_kwargs: dict) -> None:
    _test_get_endpoint(urn='/chat/history', **test_endpoint_kwargs)


def _test_get_endpoint(data: HeadersOrQueryArgsType | None = None,
                       **kwargs,
                       ) -> None:
    _test_endpoint(**kwargs, method='GET', query_args=data)


def _test_post_or_put_endpoint(data: JsonDictType | None = None,
                               **kwargs,
                               ) -> None:
    _test_endpoint(**kwargs, json_dict=data)


def _test_endpoint(urn: str,
                   method: str,
                   expected_response_status_code: HTTPStatus,
                   headers: HeadersOrQueryArgsType | None = None,
                   query_args: HeadersOrQueryArgsType | None = None,
                   json_dict: JsonDictType | None = None,
                   expected_response_json_dict: JsonDictType | None = None,
                   ) -> None:
    response: TestResponse = _test_client.open(
        urn,
        method=method,
        query_string=query_args,
        headers=headers,
        json=json_dict,
    )
    assert response.status_code == expected_response_status_code
    assert response.json == expected_response_json_dict
