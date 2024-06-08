import pytest
from http import HTTPStatus
from werkzeug.test import TestResponse

from api._tests.data.http_ import *  # must be first
from api.http_.main import app
from api._tests.common import JsonDictType, HeadersOrQueryArgsType
from api._tests.doubles import (
    HttpAppTeardownContextFunctionsListDoubleMakerForNoSessionConflictException,
    JWTJSONDictMakerMakeMethodDoubleMakerForCommonJWT,
    ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime,
    HttpSendCodeTaskFunctionDoubleMakerForNoEmailSendings,
)

_test_client = app.test_client()


def setup_module() -> None:
    HttpAppTeardownContextFunctionsListDoubleMakerForNoSessionConflictException.replace()
    JWTJSONDictMakerMakeMethodDoubleMakerForCommonJWT.replace()
    ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime.replace()
    HttpSendCodeTaskFunctionDoubleMakerForNoEmailSendings.replace()


def teardown_module() -> None:
    HttpAppTeardownContextFunctionsListDoubleMakerForNoSessionConflictException.back()
    JWTJSONDictMakerMakeMethodDoubleMakerForCommonJWT.back()
    ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime.back()
    HttpSendCodeTaskFunctionDoubleMakerForNoEmailSendings.back()


@pytest.mark.parametrize('test_endpoint_kwargs', CHECK_EMAIL_TEST_ENDPOINT_KWARGS)
def test_check_email(test_endpoint_kwargs: dict) -> None:
    _test_get_endpoint(urn='/user/login/email/check', **test_endpoint_kwargs)


@pytest.mark.parametrize('test_endpoint_kwargs', LOGIN_TEST_ENDPOINT_KWARGS)
def test_login(test_endpoint_kwargs: dict) -> None:
    _test_post_or_put_endpoint(urn='/user/login', method='POST', **test_endpoint_kwargs)


@pytest.mark.parametrize('test_endpoint_kwargs', REFRESH_TOKEN_TEST_ENDPOINT_KWARGS)
def test_refresh_token(test_endpoint_kwargs: dict) -> None:
    _test_post_or_put_endpoint(urn='/user/refreshToken', method='POST', **test_endpoint_kwargs)


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
    response: TestResponse = _test_client.open(urn, method=method,
                                               query_string=query_args, headers=headers, json=json_dict)
    assert response.status_code == expected_response_status_code
    assert response.json == expected_response_json_dict
