import pytest
from unittest.mock import patch

from db.models import User
from websocket_.validation import NewChatMessageJSONValidator
from websocket_.server_handlers import server, user_ids_and_potential_interlocutor_ids
from _tests.common.create_test_db import create_test_db
from _tests.common.assert_and_save_jsons_if_failed import assert_and_save_jsons_if_failed
from _tests.common.set_for_test_to_values_and_ids import set_for_test_to_values_and_ids
from _tests.data.websocket_ import (
    ORMObjects,
    Params,
    SetForTestCommonHandlers,
    SetForTestCommonHandlersRaises,
    SetForTestNewConnects,
    SetForTestFullDisconnects,
    SetForTestTextHandling,
)

real_output = {}


def setup_module(module) -> None:
    create_test_db(ORMObjects.users)

    def websocket_server_user_has_connections_method_mock(self, user_id: int) -> bool:
        return user_id in Params.online_user_ids

    module.ws_user_has_connections_patcher = patch('websocket_.base.server.WebSocketServer.user_has_connections',
                                                   websocket_server_user_has_connections_method_mock)
    module.ws_user_has_connections_patcher.start()

    async def websocket_server_send_to_one_user_method_mock(self, user_id: int,
                                                            message: dict,
                                                            ) -> None:
        real_output.setdefault(user_id, []).append(message)

    module.ws_send_to_one_user_patcher = patch('websocket_.base.server.WebSocketServer.send_to_one_user',
                                               websocket_server_send_to_one_user_method_mock)
    module.ws_send_to_one_user_patcher.start()

    user_ids_and_potential_interlocutor_ids.update(Params.user_ids_and_potential_interlocutor_ids)


def teardown_module(module) -> None:
    module.ws_user_has_connections_patcher.stop()
    module.ws_send_to_one_user_patcher.stop()
    user_ids_and_potential_interlocutor_ids.clear()


def teardown_function() -> None:
    real_output.clear()


@pytest.mark.parametrize(('input_', 'expected_output'), **set_for_test_to_values_and_ids(SetForTestCommonHandlers))
@pytest.mark.asyncio
async def test_handle_message(input_,
                              expected_output,
                              ) -> None:
    user, message = input_
    await server.common_handlers_funcs[message['type']](user, message['data'])
    assert_and_save_jsons_if_failed(real_output, expected_output)


@pytest.mark.parametrize(('input_', 'expected_exception'), **set_for_test_to_values_and_ids(SetForTestCommonHandlersRaises))
@pytest.mark.asyncio
async def test_handle_message_raises_exception(input_,
                                               expected_exception: type[Exception],
                                               ) -> None:
    user, message = input_
    with pytest.raises(expected_exception):
        await server.common_handlers_funcs[message['type']](user, message['data'])


@pytest.mark.parametrize(('user', 'expected_output'), **set_for_test_to_values_and_ids(SetForTestNewConnects))
@pytest.mark.asyncio
async def test_each_connection_handler(user: User,
                                       expected_output,
                                       ) -> None:
    await server.each_connection_handler_func(user)
    assert_and_save_jsons_if_failed(real_output, expected_output)


@pytest.mark.parametrize(('user', 'expected_output'), **set_for_test_to_values_and_ids(SetForTestFullDisconnects))
@pytest.mark.asyncio
async def test_full_disconnection_handler(user: User,
                                          expected_output,
                                          ) -> None:
    await server.full_disconnection_handler_func(user)
    assert_and_save_jsons_if_failed(real_output, expected_output)


@pytest.mark.parametrize(('raw_text', 'expected_text'), **set_for_test_to_values_and_ids(SetForTestTextHandling))
def test_message_text_clearing(raw_text: str,
                               expected_text: str,
                               ) -> None:
    assert NewChatMessageJSONValidator.clear_text(raw_text) == expected_text
