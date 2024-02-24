import pytest

from api._tests.websocket_test_data import *  # noqa
from api.websocket_.main import *
from api.websocket_.base import (
    ConnectAndDisconnectHandlerFuncT,
    CommonHandlerFuncT,
)

sendings = {}


def setup_module() -> None:
    server.send_to_one_user_backup = server.send_to_one_user
    server.user_have_connections_backup = server.user_have_connections

    _replace_server_send_to_one_user_method_for_check_data_to_send()
    _replace_server_user_have_one_connection_method_for_online_imitation()

    potential_interlocutors.update(POTENTIAL_INTERLOCUTORS)


def teardown_module() -> None:
    server.send_to_one_user = server.send_to_one_user_backup
    server.user_have_connections = server.user_have_connections_backup

    potential_interlocutors.clear()


def _replace_server_send_to_one_user_method_for_check_data_to_send() -> None:

    async def method(user_id: int,
                     message: dict,
                     ) -> None:
        sendings.setdefault(user_id, []).append(message)

    server.send_to_one_user = method


def _replace_server_user_have_one_connection_method_for_online_imitation() -> None:

    def method(user_id: int) -> bool:
        return user_id in ONLINE_USERS_IDS

    server.user_have_connections = method


async def _test_positive_handler_and_sendings(handler_func: ConnectAndDisconnectHandlerFuncT | CommonHandlerFuncT,
                                              handler_kwargs: dict,
                                              expected_sendings,
                                              ) -> None:
    sendings.clear()
    await handler_func(**handler_kwargs)
    assert sendings == expected_sendings


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), FIRST_CONNECTION_HANDLER_SENDINGS)
@pytest.mark.asyncio
async def test_positive_first_connection_handler(handler_kwargs: dict,
                                                 expected_sendings,
                                                 ) -> None:
    await _test_positive_handler_and_sendings(first_connection_handler, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), FULL_DISCONNECTION_HANDLER_SENDINGS)
@pytest.mark.asyncio
async def test_positive_full_disconnection_handler(handler_kwargs: dict,
                                                   expected_sendings,
                                                   ) -> None:
    await _test_positive_handler_and_sendings(full_disconnection_handler, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), ONLINE_STATUS_TRACING_ADDING_HANDLER_SENDINGS)
@pytest.mark.asyncio
async def test_positive_online_status_tracing_adding_handler(handler_kwargs: dict,
                                                             expected_sendings,
                                                             ) -> None:
    await _test_positive_handler_and_sendings(new_interlocutor_online_status_adding, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), NEW_CHAT_HANDLER_SENDINGS)
@pytest.mark.asyncio
async def test_positive_new_chat_handler(handler_kwargs: dict,
                                         expected_sendings,
                                         ) -> None:
    await _test_positive_handler_and_sendings(new_chat, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), NEW_CHAT_MESSAGE_HANDLER_SENDINGS)
@pytest.mark.asyncio
async def test_positive_new_chat_message_handler(handler_kwargs: dict,
                                                 expected_sendings,
                                                 ) -> None:
    await _test_positive_handler_and_sendings(new_chat_message, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), NEW_CHAT_MESSAGE_TYPING_HANDLER_SENDINGS)
@pytest.mark.asyncio
async def test_positive_new_chat_message_typing_handler(handler_kwargs: dict,
                                                        expected_sendings,
                                                        ) -> None:
    await _test_positive_handler_and_sendings(new_chat_message_typing, handler_kwargs, expected_sendings)
