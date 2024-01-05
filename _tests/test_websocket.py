import pytest
from websockets import WebSocketServerProtocol

from api.websocket_.base import (
    WebSocketServer,
    WebSocketClientHandler,
)
from api.websocket_.main_ import new_chat_message, new_chat
from api._tests.db_test_data import *  # noqa


class WebSocketServerProtocolStub(WebSocketServerProtocol):

    def __init__(self) -> None:  # noqa
        pass


class TestWebSocketServer:
    server = WebSocketServer(
        'localhost', 2220
    )

    @classmethod
    @pytest.mark.parametrize('attr_name', [
        'host',
        'port',
        'run',
        '_handler',
        '_add_client',
        '_del_client',
        'send_to_many_users',
    ])
    def test_positive_instance_has_attr(cls, attr_name: str) -> None:
        assert hasattr(cls.server, attr_name)


class TestWebSocketClientHandler:
    client = WebSocketClientHandler(
        TestWebSocketServer.server,
        WebSocketServerProtocolStub(),
    )

    @classmethod
    @pytest.mark.parametrize('attr_name', [
        'server',
        'protocol',
        'auth',
        'listen',
    ])
    def test_positive_instance_has_attr(cls, attr_name: str) -> None:
        assert hasattr(cls.client, attr_name)
