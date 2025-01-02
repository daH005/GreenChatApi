import pytest
from unittest.mock import patch

from db.models import User
from websocket_.common import clear_message_text
from websocket_.server_handlers import server, users_ids_and_potential_interlocutors_ids
from _tests.common.create_test_db import create_test_db
from _tests.common.assert_and_save_jsons_if_failed import assert_and_save_jsons_if_failed
from _tests.data.websocket_ import (
    ORMObjects,
    Params,
    SetForTest,
)

real_output = {}


def setup_module() -> None:
    create_test_db(ORMObjects.users)

    def websocket_server_user_have_connections_method_mock(self, user_id: int) -> bool:
        return user_id in Params.online_user_ids

    patch('websocket_.base.server.WebSocketServer.user_have_connections',
          websocket_server_user_have_connections_method_mock).start()

    async def websocket_server_send_to_one_user_method_mock(self, user_id: int,
                                                            message: dict,
                                                            ) -> None:
        real_output.setdefault(user_id, []).append(message)

    patch('websocket_.base.server.WebSocketServer.send_to_one_user',
          websocket_server_send_to_one_user_method_mock).start()

    users_ids_and_potential_interlocutors_ids.update(Params.user_ids_and_potential_interlocutor_ids)


def teardown_module() -> None:
    patch('websocket_.base.server.WebSocketServer.user_have_connections').stop()
    patch('websocket_.base.server.WebSocketServer.send_to_one_user').stop()
    users_ids_and_potential_interlocutors_ids.clear()


def teardown_function() -> None:
    real_output.clear()


@pytest.mark.parametrize(('input_', 'expected_output'), SetForTest.all_input_and_output)
@pytest.mark.asyncio
async def test_handle_message(input_,
                              expected_output,
                              ) -> None:
    user, message = input_
    await server.common_handlers_funcs[message['type']](user, message['data'])
    assert_and_save_jsons_if_failed(real_output, expected_output)


@pytest.mark.parametrize(('input_', 'expected_exception'), SetForTest.all_input_and_raises)
@pytest.mark.asyncio
async def test_handle_message_raises_exception(input_,
                                               expected_exception: type[Exception],
                                               ) -> None:
    user, message = input_
    with pytest.raises(expected_exception):
        await server.common_handlers_funcs[message['type']](user, message['data'])


@pytest.mark.parametrize(('user', 'expected_output'), SetForTest.new_connects)
@pytest.mark.asyncio
async def test_each_connection_handler(user: User,
                                       expected_output,
                                       ) -> None:
    await server.each_connection_handler_func(user)
    assert_and_save_jsons_if_failed(real_output, expected_output)


@pytest.mark.parametrize(('user', 'expected_output'), SetForTest.full_disconnects)
@pytest.mark.asyncio
async def test_full_disconnection_handler(user: User,
                                          expected_output,
                                          ) -> None:
    await server.full_disconnection_handler_func(user)
    assert_and_save_jsons_if_failed(real_output, expected_output)


@pytest.mark.parametrize(('raw_text', 'expected_text'), SetForTest.raw_and_handled_texts)
def test_message_text_clearing(raw_text: str,
                               expected_text: str,
                               ) -> None:
    assert clear_message_text(raw_text) == expected_text
