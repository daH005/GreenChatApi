from __future__ import annotations
import asyncio
from websockets import WebSocketServerProtocol, serve, ConnectionClosed  # pip install websockets
from typing import NoReturn, Callable, TypedDict
import json
from json import JSONDecodeError
from jwt import decode  # pip install pyjwt

from api.db.models import User, session
from api.raises_hinting import raises
from api.config import JWT_SECRET_KEY, JWT_ALGORITHM
from api.websocket_.funcs import UserID
from api.websocket_.logs import logger

__all__ = (
    'WebSocketServer',
    'WebSocketClientHandler',
    'HandlerFuncT',
    'HandlerFuncReturnT',
)

HandlerFuncReturnT = tuple[list[UserID], dict]
HandlerFuncT = Callable[[User, dict], HandlerFuncReturnT]
TYPE_KEY = 'type'
DATA_KEY = 'data'


class MessageJSONDict(TypedDict):

    type: str
    data: dict


class WebSocketServer:

    def __init__(self, host: str,
                 port: int,
                 ) -> None:
        self.host = host
        self.port = port
        self._clients: dict[UserID, list[WebSocketClientHandler]] = {}
        self.handlers_funcs: dict[str, HandlerFuncT] = {}

    def run(self) -> NoReturn:
        asyncio.run(self._run())

    async def _run(self) -> NoReturn:
        async with serve(ws_handler=self._handler, host=self.host, port=self.port):
            await asyncio.Future()  # run forever

    async def _handler(self, protocol: WebSocketServerProtocol) -> None:
        logger.info(f'New client connected - {protocol.id}. Waiting authorization...')
        try:
            await self._handle_protocol(protocol)
        except (ConnectionClosed, ValueError):
            logger.info(f'Client disconnected ({protocol.id}).')
            return

    async def _handle_protocol(self, protocol: WebSocketServerProtocol) -> None:
        client = WebSocketClientHandler(self, protocol)
        await client.auth()
        logger.info(f'Client was auth ({protocol.id}). UserID - {client.user.id}.')

        self._add_client(client)

        try:
            await client.listen()
        except ConnectionClosed:
            self._del_client(client)
            raise

    def _add_client(self, client: WebSocketClientHandler) -> None:
        self._clients.setdefault(client.user.id, []).append(client)

    def _del_client(self, client: WebSocketClientHandler) -> None:
        try:
            self._clients[client.user.id].remove(client)
        except (KeyError, ValueError):
            return

    async def send_to_many_users(self, users_ids: list[UserID],
                                 message: MessageJSONDict,
                                 ) -> None:
        for id_ in users_ids:
            if id_ not in self._clients:
                continue
            await self.send_to_one_user(id_, message)

    async def send_to_one_user(self, user_id: UserID,
                               message: MessageJSONDict,
                               ) -> None:
        for client in self._clients[user_id]:
            await self.send_to_one_client(client, message)

    @staticmethod
    async def send_to_one_client(client: WebSocketClientHandler,
                                 message: MessageJSONDict,
                                 ) -> None:
        try:
            await client.protocol.send(json.dumps(message))
        except ConnectionClosed:
            return

    def handler(self, type_: str) -> Callable[[HandlerFuncT], HandlerFuncT]:
        def func_decorator(func: HandlerFuncT) -> HandlerFuncT:
            self.handlers_funcs[type_] = func
            return func
        return func_decorator


class WebSocketClientHandler:

    def __init__(self, server: WebSocketServer,
                 protocol: WebSocketServerProtocol,
                 ) -> None:
        self.server = server
        self.protocol = protocol
        self.user: User | None = None

    @raises(ConnectionClosed, ValueError)
    async def auth(self) -> None:
        jwt_token: str = await self._wait_str()
        auth_token: str = self._decode_jwt(encoded=jwt_token)
        self._try_auth_user(auth_token=auth_token)

    @staticmethod
    def _decode_jwt(encoded: str) -> str:
        return decode(
            encoded,
            key=JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )['sub']

    @raises(ValueError)
    def _try_auth_user(self, auth_token: str) -> None:
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
                self._handle_message(message)
            except (JSONDecodeError, KeyError, Exception):
                continue
            session.remove()
    
    @raises(JSONDecodeError, KeyError, Exception)
    def _handle_message(self, message: MessageJSONDict) -> None:
        handler_func: HandlerFuncT = self._get_handler_func(message[TYPE_KEY])
        users_ids, data = handler_func(self.user, message[DATA_KEY])

        _message: MessageJSONDict = {  # type: ignore
            TYPE_KEY: message[TYPE_KEY],
            DATA_KEY: data,
        }
        self.server.send_to_many_users(users_ids=users_ids, message=_message)

    @raises(KeyError)
    def _get_handler_func(self, type_: str) -> HandlerFuncT:
        return self.server.handlers_funcs[type_]
