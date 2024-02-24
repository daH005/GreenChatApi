import pytest

from api._tests.websocket_test_data import *  # noqa
from api.websocket_.main import *
from api.websocket_.base import (
    ConnectAndDisconnectHandlerFuncT,
    CommonHandlerFuncT,
)

sendings = {}


def setup_module() -> None:
    replace_send_to_one_user_method_for_check_data_to_send()
    replace_user_have_one_connection_method_for_online_imitation()


def replace_send_to_one_user_method_for_check_data_to_send() -> None:

    async def method(user_id: int,
                     message: dict,
                     ) -> None:
        sendings.setdefault(user_id, []).append(message)

    server.send_to_one_user = method


def replace_user_have_one_connection_method_for_online_imitation() -> None:

    async def method(user_id: int) -> bool:
        return user_id in ONLINE_USERS_IDS

    server.user_have_connections = method


async def _test_positive_handler_and_sendings(handler_func: ConnectAndDisconnectHandlerFuncT | CommonHandlerFuncT,
                                              handler_kwargs: dict,
                                              expected_sendings,
                                              ) -> None:
    sendings.clear()
    await handler_func(**handler_kwargs)
    assert sendings == expected_sendings


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), FIRST_CONNECTION_HANDLER_SENT_DATA)
@pytest.mark.asyncio
async def test_positive_first_connection_handler(handler_kwargs: dict,
                                                 expected_sendings,
                                                 ) -> None:
    await _test_positive_handler_and_sendings(first_connection_handler, handler_kwargs, expected_sendings)
