from __future__ import annotations
import asyncio
from websockets import WebSocketServerProtocol, serve, ConnectionClosed  # pip install websockets
from typing import NoReturn, Callable, Coroutine
import json
from json import JSONDecodeError
from jwt import decode  # pip install pyjwt

from api.db.models import User, session
from api.hinting import raises
from api.config import JWT_SECRET_KEY, JWT_ALGORITHM
from api.websocket_.logs import logger, init_logs
from api.websocket_.messages import (
    MessageJSONDict,
    JSONKey,
)

__all__ = (
    'WebSocketServer',
    'WebSocketClientHandler',
    'CommonHandlerFuncT',
    'ConnectAndDisconnectHandlerFuncT',
)

CommonHandlerFuncT = Callable[[User, dict], Coroutine]
ConnectAndDisconnectHandlerFuncT = Callable[[User], Coroutine]


class WebSocketServer:

    def __init__(self, host: str,
                 port: int,
                 ) -> None:
        self.host = host
        self.port = port
        self._clients: dict[int, list[WebSocketClientHandler]] = {}
        self.common_handlers_funcs: dict[str, CommonHandlerFuncT] = {}

    def run(self) -> NoReturn:
        init_logs()  # Решено остановиться здесь из-за мерзкой реализации логов `alembic`
        asyncio.run(self._run())

    async def _run(self) -> NoReturn:
        async with serve(ws_handler=self._handler, host=self.host, port=self.port):
            logger.info('WebSocketServer is serving...')
            await asyncio.Future()  # run forever

    async def _handler(self, protocol: WebSocketServerProtocol) -> None:
        logger.info(f'New client connected - {protocol.id}. Waiting authorization...')
        try:
            await self._handle_protocol(protocol)
        except ConnectionClosed:
            pass
        logger.info(f'Client disconnected ({protocol.id}).')

    @raises(ConnectionClosed)
    async def _handle_protocol(self, protocol: WebSocketServerProtocol) -> None:
        client = WebSocketClientHandler(self, protocol)
        await client.auth()
        logger.info(f'Client was auth ({protocol.id}). UserID - {client.user.id}.')

        self._add_client(client)
        if self._user_have_only_one_connection(client.user.id):
            await self._first_connection_handler(client.user)

        try:
            await client.listen()
        except ConnectionClosed:
            self._del_client(client)
            if not self.user_have_connections(client.user.id):
                await self._full_disconnection_handler(client.user)

            raise

    def _add_client(self, client: WebSocketClientHandler) -> None:
        self._clients.setdefault(client.user.id, []).append(client)

    def _del_client(self, client: WebSocketClientHandler) -> None:
        try:
            self._clients[client.user.id].remove(client)
        except (KeyError, ValueError):
            return

    def _user_have_only_one_connection(self, used_id: int) -> bool:
        return len(self._clients.get(used_id, [])) == 1

    def user_have_connections(self, used_id: int) -> bool:
        return len(self._clients.get(used_id, [])) != 0

    async def send_to_many_users(self, users_ids: list[int] | set[int],
                                 message: MessageJSONDict,
                                 ) -> None:
        users_ids = set(users_ids)
        for id_ in users_ids:
            await self.send_to_one_user(id_, message)

    async def send_to_one_user(self, user_id: int,
                               message: MessageJSONDict,
                               ) -> None:
        for client in self._clients.get(user_id, []):
            await self.send_to_one_client(client, message)

    @staticmethod
    async def send_to_one_client(client: WebSocketClientHandler,
                                 message: MessageJSONDict,
                                 ) -> None:
        try:
            await client.protocol.send(json.dumps(message))
        except ConnectionClosed:
            return

    def common_handler(self, type_: str) -> Callable[[CommonHandlerFuncT], CommonHandlerFuncT]:
        def func_decorator(func: CommonHandlerFuncT) -> CommonHandlerFuncT:
            self.common_handlers_funcs[type_] = func
            return func
        return func_decorator

    def first_connection_handler(self, func: ConnectAndDisconnectHandlerFuncT) -> ConnectAndDisconnectHandlerFuncT:
        self._first_connection_handler = func  # noqa
        return func

    @staticmethod
    async def _first_connection_handler(user: User) -> None:
        pass

    def full_disconnection_handler(self, func: ConnectAndDisconnectHandlerFuncT) -> ConnectAndDisconnectHandlerFuncT:
        self._full_disconnection_handler = func  # noqa
        return func

    @staticmethod
    async def _full_disconnection_handler(user: User) -> None:
        pass


class WebSocketClientHandler:

    def __init__(self, server: WebSocketServer,
                 protocol: WebSocketServerProtocol,
                 ) -> None:
        self.server = server
        self.protocol = protocol
        self.user: User | None = None

    @raises(ConnectionClosed)
    async def auth(self) -> None:
        jwt_token: str = await self._wait_str()
        auth_token: str = self._decode_jwt(encoded=jwt_token)
        try:
            self._try_auth_user(auth_token=auth_token)
        except ValueError:
            await self.auth()

    @staticmethod
    def _decode_jwt(encoded: str) -> str:
        return decode(
            encoded,
            key=JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )['sub']

    @raises(ValueError)
    def _try_auth_user(self, auth_token: str) -> None:
        session.remove()  # for session updating
        self.user = User.auth_by_token(auth_token=auth_token)

    @raises(ConnectionClosed)
    async def _wait_str(self) -> str:
        return await self.protocol.recv()

    @raises(ConnectionClosed, JSONDecodeError)
    async def _wait_json_dict(self) -> MessageJSONDict:
        return json.loads(await self._wait_str())

    @raises(ConnectionClosed)
    async def listen(self) -> None:
        while True:
            try:
                message: MessageJSONDict = await self._wait_json_dict()
            except JSONDecodeError:
                continue

            try:
                await self._handle_message(message)
            except Exception as e:
                msg = (f'Handling error ({type(e).__name__}):\n'
                       f'- Message:\n'
                       f'{json.dumps(message, indent=4)}\n'
                       f'- UserID: {self.user.id} ({self.protocol.id})')
                logger.info(msg)
                continue

            session.remove()

    @raises(KeyError, Exception)
    async def _handle_message(self, message: MessageJSONDict) -> None:
        handler_func: CommonHandlerFuncT = self._get_handler_func(message[JSONKey.TYPE])  # type: ignore
        await handler_func(user=self.user, data=message[JSONKey.DATA])  # type: ignore
        logger.info(f'\"{message[JSONKey.TYPE]}\". '  # type: ignore
                    f'UserID - {self.user.id} ({self.protocol.id}).')

    @raises(KeyError)
    def _get_handler_func(self, type_: str) -> CommonHandlerFuncT:
        return self.server.common_handlers_funcs[type_]
