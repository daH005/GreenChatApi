import pytest
from datetime import datetime  # noqa

from api._tests.data.websocket_ import *  # must be first!
from api.websocket_.main import *
from api.websocket_.base import (
    ConnectAndDisconnectHandlerFuncT,
    CommonHandlerFuncT,
)
from api.websocket_.funcs import clear_message_text
from api._tests.replacing import (
    ChatMessageJSONDictMakerMakeMethodReplacerForCommonDatetime,
    ServerSendToOneUserMethodReplacerForServerMessagesStorage,
    ServerUserHaveConnectionsMethodReplacerForOnlineImitation,
)


def setup_module() -> None:
    ChatMessageJSONDictMakerMakeMethodReplacerForCommonDatetime.replace()
    ServerSendToOneUserMethodReplacerForServerMessagesStorage.replace()
    ServerUserHaveConnectionsMethodReplacerForOnlineImitation.replace()

    users_ids_and_potential_interlocutors_ids.update(USERS_IDS_AND_POTENTIAL_INTERLOCUTORS_IDS)


def teardown_module() -> None:
    ChatMessageJSONDictMakerMakeMethodReplacerForCommonDatetime.back()
    ServerSendToOneUserMethodReplacerForServerMessagesStorage.back()
    ServerUserHaveConnectionsMethodReplacerForOnlineImitation.back()

    users_ids_and_potential_interlocutors_ids.clear()


async def _test_positive_handler_and_sendings(handler_func: ConnectAndDisconnectHandlerFuncT | CommonHandlerFuncT,
                                              handler_kwargs: dict,
                                              expected_sendings,
                                              ) -> None:
    ServerSendToOneUserMethodReplacerForServerMessagesStorage.sendings.clear()
    await handler_func(**handler_kwargs)
    assert ServerSendToOneUserMethodReplacerForServerMessagesStorage.sendings == expected_sendings


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), EACH_CONNECTION_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_each_connection_handler(handler_kwargs: dict,
                                                expected_sendings,
                                                ) -> None:
    await _test_positive_handler_and_sendings(each_connection_handler, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), FULL_DISCONNECTION_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_full_disconnection_handler(handler_kwargs: dict,
                                                   expected_sendings,
                                                   ) -> None:
    await _test_positive_handler_and_sendings(full_disconnection_handler, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), ONLINE_STATUS_TRACING_ADDING_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_online_status_tracing_adding_handler(handler_kwargs: dict,
                                                             expected_sendings,
                                                             ) -> None:
    await _test_positive_handler_and_sendings(online_status_tracing_adding, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), NEW_CHAT_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_new_chat_handler(handler_kwargs: dict,
                                         expected_sendings,
                                         ) -> None:
    await _test_positive_handler_and_sendings(new_chat, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), NEW_CHAT_MESSAGE_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_new_chat_message_handler(handler_kwargs: dict,
                                                 expected_sendings,
                                                 ) -> None:
    await _test_positive_handler_and_sendings(new_chat_message, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), NEW_CHAT_MESSAGE_TYPING_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_new_chat_message_typing_handler(handler_kwargs: dict,
                                                        expected_sendings,
                                                        ) -> None:
    await _test_positive_handler_and_sendings(new_chat_message_typing, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('handler_kwargs', 'expected_sendings'), CHAT_MESSAGE_WAS_READ_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_chat_message_was_read_handler(handler_kwargs: dict,
                                                      expected_sendings,
                                                      ) -> None:
    await _test_positive_handler_and_sendings(chat_message_was_read, handler_kwargs, expected_sendings)


@pytest.mark.parametrize(('raw_text', 'expected_text'), RAW_AND_HANDLED_MESSAGES_TEXTS)
def test_positive_message_text_clearing(raw_text: str,
                                        expected_text: str,
                                        ) -> None:
    assert clear_message_text(raw_text) == expected_text
