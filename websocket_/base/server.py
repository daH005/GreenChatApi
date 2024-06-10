import asyncio
from typing import NoReturn, Callable
from websockets import serve, WebSocketServerProtocol, ConnectionClosed

from api.common.hinting import raises
from api.common.json_ import WebSocketMessageJSONDictMaker
from api.db.models import User
from api.websocket_.base.typing_ import CommonHandlerFuncT, ConnectAndDisconnectHandlerFuncT
from api.websocket_.base.client_handler import WebSocketClientHandler
from api.websocket_.base.logs import init_logs, logger

__all__ = (
    'WebSocketServer',
)


class WebSocketServer:

    def __init__(self, host: str, port: int,
                 jwt_secret_key: str, jwt_algorithm: str,
                 ) -> None:
        self._host = host
        self._port = port
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm

        self._clients: dict[int, list[WebSocketClientHandler]] = {}
        self._common_handlers_funcs: dict[str, CommonHandlerFuncT] = {}

    def run(self) -> NoReturn:
        init_logs()  # The place chosen by experience way
        asyncio.run(self._run())

    async def _run(self) -> NoReturn:
        async with serve(ws_handler=self._handler, host=self._host, port=self._port):
            logger.info(f'WebSocketServer is serving on ws://{self._host}:{self._port}')
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
        client = WebSocketClientHandler(
            protocol=protocol,
            common_handlers_funcs=self._common_handlers_funcs,
            jwt_secret_key=self._jwt_secret_key,
            jwt_algorithm=self._jwt_algorithm,
        )
        await client.wait_authorization()
        logger.info(f'[{client.user.id}] Client was authorized.')

        self._add_client(client)
        await self._each_connection_handler(client.user)

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

    def user_have_connections(self, user_id: int) -> bool:
        return len(self._clients.get(user_id, [])) != 0

    async def send_to_many_users(self, users_ids: list[int] | set[int],
                                 message: WebSocketMessageJSONDictMaker.Dict,
                                 ) -> None:
        users_ids = set(users_ids)
        for id_ in users_ids:
            await self.send_to_one_user(id_, message)

    async def send_to_one_user(self, user_id: int,
                               message: WebSocketMessageJSONDictMaker.Dict,
                               ) -> None:
        for client in self._clients.get(user_id, []):
            await self.send_to_one_client(client, message)

    @staticmethod
    async def send_to_one_client(client: WebSocketClientHandler,
                                 message: WebSocketMessageJSONDictMaker.Dict,
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
