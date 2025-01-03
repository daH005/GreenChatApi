import asyncio
from ssl import SSLContext
from typing import NoReturn, Callable, Final
from websockets import serve, WebSocketServerProtocol, ConnectionClosed
import re
from jwt import decode as decode_jwt

from common.hinting import raises
from websocket_.base.websocket_message import WebSocketMessageJSONDict
from db.builder import db_builder
from db.models import User
from websocket_.base.typing_ import CommonHandlerFuncT, ConnectAndDisconnectHandlerFuncT
from websocket_.base.client_handler import WebSocketClientHandler
from websocket_.base.logs import init_logs, logger

__all__ = (
    'WebSocketServer',
)


class WebSocketServer:
    _RE_TO_EXTRACT_JWT_FROM_COOKIES: Final[str] = 'access_token_cookie=([^;]*);?'

    def __init__(self, host: str, port: int,
                 jwt_secret_key: str, jwt_algorithm: str,
                 ssl_context: SSLContext,
                 ) -> None:
        self._host = host
        self._port = port
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm
        self._ssl_context = ssl_context

        self._clients: dict[int, list[WebSocketClientHandler]] = {}
        self._common_handlers_funcs: dict[str, CommonHandlerFuncT] = {}

    def run(self) -> NoReturn:
        init_logs()  # The place chosen by experience way
        asyncio.run(self._run())

    async def _run(self) -> NoReturn:
        async with serve(ws_handler=self._handler, host=self._host, port=self._port, ssl=self._ssl_context):
            logger.info(f'WebSocketServer is serving on wss://{self._host}:{self._port}')
            await asyncio.Future()  # run forever

    async def _handler(self, protocol: WebSocketServerProtocol) -> None:
        logger.info(f'New client connected. Waiting authorization...')
        try:
            await self._handle_protocol(protocol)
        except ConnectionClosed:
            pass
        logger.info(f'Client disconnected.')

    @raises(ConnectionClosed)
    async def _handle_protocol(self, protocol: WebSocketServerProtocol) -> None:
        if 'Cookie' not in protocol.request_headers:
            return

        try:
            jwt: str = self._extract_jwt_from_cookies(protocol.request_headers['Cookie'])
        except ValueError:
            return

        try:
            user_id: int = self._try_to_get_user_id_by_jwt(jwt)
        except ValueError:
            return

        client = WebSocketClientHandler(
            protocol=protocol,
            common_handlers_funcs=self._common_handlers_funcs,
            user_id=user_id,
        )
        logger.info(f'[{client.user.id}] Client was authorized.')

        self._add_client(client)
        await self._each_connection_handler(client.user)

        try:
            await client.listen()
        except ConnectionClosed:
            self._del_client(client)
            if not self.user_has_connections(client.user.id):
                await self._full_disconnection_handler(client.user)
            raise

    @raises(ValueError)
    def _extract_jwt_from_cookies(self, cookies: str) -> str:
        match = re.search(self._RE_TO_EXTRACT_JWT_FROM_COOKIES, cookies)
        if not match:
            raise ValueError
        return match.group(1)

    @raises(ValueError)
    def _try_to_get_user_id_by_jwt(self, jwt: str) -> int:
        email: str = self._try_to_get_email_from_jwt(jwt)
        db_builder.session.remove()  # for session updating
        return User.by_email(email=email).id

    @raises(ValueError)
    def _try_to_get_email_from_jwt(self, jwt: str) -> str:
        try:
            decoded: dict = decode_jwt(
                jwt,
                key=self._jwt_secret_key,
                algorithms=[self._jwt_algorithm],
            )
            return decoded['sub']
        except KeyError:
            raise ValueError

    def _add_client(self, client: WebSocketClientHandler) -> None:
        self._clients.setdefault(client.user.id, []).append(client)

    def _del_client(self, client: WebSocketClientHandler) -> None:
        try:
            self._clients[client.user.id].remove(client)
        except (KeyError, ValueError):
            return

    def user_has_connections(self, user_id: int) -> bool:
        return len(self._clients.get(user_id, [])) != 0

    async def send_to_many_users(self, user_ids: list[int] | set[int],
                                 message: WebSocketMessageJSONDict,
                                 ) -> None:
        user_ids = set(user_ids)
        for id_ in user_ids:
            await self.send_to_one_user(id_, message)

    async def send_to_one_user(self, user_id: int,
                               message: WebSocketMessageJSONDict,
                               ) -> None:
        for client in self._clients.get(user_id, []):
            await self.send_to_one_client(client, message)

    @staticmethod
    async def send_to_one_client(client: WebSocketClientHandler,
                                 message: WebSocketMessageJSONDict,
                                 ) -> None:
        try:
            await client.send(message)
        except ConnectionClosed:
            return

    def common_handler(self, type_: str) -> Callable[[CommonHandlerFuncT], CommonHandlerFuncT]:
        def func_decorator(func: CommonHandlerFuncT) -> CommonHandlerFuncT:
            self._common_handlers_funcs[type_] = func
            return func
        return func_decorator

    def each_connection_handler(self, func: ConnectAndDisconnectHandlerFuncT) -> ConnectAndDisconnectHandlerFuncT:
        self._each_connection_handler = func  # noqa
        return func

    @staticmethod
    async def _each_connection_handler(user: User) -> None:
        pass

    def full_disconnection_handler(self, func: ConnectAndDisconnectHandlerFuncT) -> ConnectAndDisconnectHandlerFuncT:
        self._full_disconnection_handler = func  # noqa
        return func

    @staticmethod
    async def _full_disconnection_handler(user: User) -> None:
        pass

    @property
    def each_connection_handler_func(self):
        return self._each_connection_handler

    @property
    def full_disconnection_handler_func(self):
        return self._full_disconnection_handler

    @property
    def common_handlers_funcs(self):
        return self._common_handlers_funcs
