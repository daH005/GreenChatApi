import pytest

from api._tests.data.websocket_ import *  # must be first!
from api.websocket_.main import *
from api.websocket_.base.typing_ import CommonHandlerFuncT, ConnectAndDisconnectHandlerFuncT
from api.websocket_.common import clear_message_text
from api._tests.doubles import (
    ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime,
    WebsocketServerSendToOneUserMethodDoubleMakerForServerMessagesStorage,
    WebsocketServerUserHaveConnectionsMethodDoubleMakerForOnlineImitation,
)


def setup_module() -> None:
    ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime.replace()
    WebsocketServerSendToOneUserMethodDoubleMakerForServerMessagesStorage.replace()
    WebsocketServerUserHaveConnectionsMethodDoubleMakerForOnlineImitation.replace()

    users_ids_and_potential_interlocutors_ids.update(USERS_IDS_AND_POTENTIAL_INTERLOCUTORS_IDS)


def teardown_module() -> None:
    ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime.back()
    WebsocketServerSendToOneUserMethodDoubleMakerForServerMessagesStorage.back()
    WebsocketServerUserHaveConnectionsMethodDoubleMakerForOnlineImitation.back()

    users_ids_and_potential_interlocutors_ids.clear()


@pytest.mark.parametrize(('handler_kwargs', 'expected_server_messages'),
                         EACH_CONNECTION_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_each_connection_handler(handler_kwargs: dict,
                                                expected_server_messages,
                                                ) -> None:
    await _test_positive_handler_and_server_messages(each_connection_handler, handler_kwargs, expected_server_messages)


@pytest.mark.parametrize(('handler_kwargs', 'expected_server_messages'),
                         FULL_DISCONNECTION_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_full_disconnection_handler(handler_kwargs: dict,
                                                   expected_server_messages,
                                                   ) -> None:
    await _test_positive_handler_and_server_messages(full_disconnection_handler, handler_kwargs,
                                                     expected_server_messages)


@pytest.mark.parametrize(('handler_kwargs', 'expected_server_messages'),
                         ONLINE_STATUS_TRACING_ADDING_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_online_status_tracing_adding_handler(handler_kwargs: dict,
                                                             expected_server_messages,
                                                             ) -> None:
    await _test_positive_handler_and_server_messages(online_status_tracing_adding, handler_kwargs,
                                                     expected_server_messages)


@pytest.mark.parametrize(('handler_kwargs', 'expected_server_messages'), NEW_CHAT_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_new_chat_handler(handler_kwargs: dict,
                                         expected_server_messages,
                                         ) -> None:
    await _test_positive_handler_and_server_messages(new_chat, handler_kwargs, expected_server_messages)


@pytest.mark.parametrize(('handler_kwargs', 'expected_exception'), NEW_CHAT_HANDLER_KWARGS_AND_EXCEPTIONS)
@pytest.mark.asyncio
async def test_negative_new_chat_handler(handler_kwargs: dict,
                                         expected_exception: type[Exception],
                                         ) -> None:
    with pytest.raises(expected_exception):
        await new_chat(**handler_kwargs)


@pytest.mark.parametrize(('handler_kwargs', 'expected_server_messages'),
                         NEW_CHAT_MESSAGE_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_new_chat_message_handler(handler_kwargs: dict,
                                                 expected_server_messages,
                                                 ) -> None:
    await _test_positive_handler_and_server_messages(new_chat_message, handler_kwargs, expected_server_messages)


@pytest.mark.parametrize(('handler_kwargs', 'expected_exception'), NEW_CHAT_MESSAGE_HANDLER_KWARGS_AND_EXCEPTIONS)
@pytest.mark.asyncio
async def test_negative_new_chat_message_handler(handler_kwargs: dict,
                                                 expected_exception: type[Exception],
                                                 ) -> None:
    with pytest.raises(expected_exception):
        await new_chat_message(**handler_kwargs)


@pytest.mark.parametrize(('handler_kwargs', 'expected_server_messages'),
                         NEW_CHAT_MESSAGE_TYPING_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_new_chat_message_typing_handler(handler_kwargs: dict,
                                                        expected_server_messages,
                                                        ) -> None:
    await _test_positive_handler_and_server_messages(new_chat_message_typing, handler_kwargs, expected_server_messages)


@pytest.mark.parametrize(('handler_kwargs', 'expected_exception'), NEW_CHAT_MESSAGE_TYPING_HANDLER_KWARGS_AND_EXCEPTIONS)
@pytest.mark.asyncio
async def test_negative_new_chat_message_typing_handler(handler_kwargs: dict,
                                                        expected_exception: type[Exception],
                                                        ) -> None:
    with pytest.raises(expected_exception):
        await new_chat_message_typing(**handler_kwargs)


@pytest.mark.parametrize(('handler_kwargs', 'expected_server_messages'),
                         CHAT_MESSAGE_WAS_READ_HANDLER_KWARGS_AND_SERVER_MESSAGES)
@pytest.mark.asyncio
async def test_positive_chat_message_was_read_handler(handler_kwargs: dict,
                                                      expected_server_messages,
                                                      ) -> None:
    await _test_positive_handler_and_server_messages(chat_message_was_read, handler_kwargs, expected_server_messages)


@pytest.mark.parametrize(('handler_kwargs', 'expected_exception'), CHAT_MESSAGE_WAS_READ_HANDLER_KWARGS_AND_EXCEPTIONS)
@pytest.mark.asyncio
async def test_negative_chat_message_was_read_handler(handler_kwargs: dict,
                                                      expected_exception: type[Exception],
                                                      ) -> None:
    with pytest.raises(expected_exception):
        await chat_message_was_read(**handler_kwargs)


@pytest.mark.parametrize(('raw_text', 'expected_text'), RAW_AND_HANDLED_MESSAGES_TEXTS)
def test_positive_message_text_clearing(raw_text: str,
                                        expected_text: str,
                                        ) -> None:
    assert clear_message_text(raw_text) == expected_text


async def _test_positive_handler_and_server_messages(
        handler_func: ConnectAndDisconnectHandlerFuncT | CommonHandlerFuncT,
        handler_kwargs: dict,
        expected_server_messages,
        ) -> None:
    WebsocketServerSendToOneUserMethodDoubleMakerForServerMessagesStorage.saved_server_messages.clear()
    await handler_func(**handler_kwargs)
    assert WebsocketServerSendToOneUserMethodDoubleMakerForServerMessagesStorage.saved_server_messages == expected_server_messages
