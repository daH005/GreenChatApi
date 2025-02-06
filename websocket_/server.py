import asyncio
import json
import re
from ssl import SSLContext
from typing import NoReturn, Final

from jwt import decode as decode_jwt, PyJWTError
from websockets import (
    serve,
    WebSocketServerProtocol,
    ConnectionClosed,
)

from common.hinting import raises
from common.json_keys import JSONKey
from common.online_set import OnlineSet
from common.signals.message import SignalQueueMessage, SignalQueueMessageJSONDictToForward
from common.signals.queue import SignalQueue
from common.signals.signal_types import SignalType
from common.signals.exceptions import SignalQueueIsEmptyException
from db.builder import db_builder
from db.exceptions import DBEntityNotFoundException
from db.models import User, UserChatMatch
from websocket_.logs import init_logs, logger
from websocket_.exceptions import (
    InvalidOriginException,
    JWTNotFoundInCookiesException,
    UserIdNotFoundInJWTException,
)

__all__ = (
    'WebSocketServer',
)


class WebSocketServer:
    _RE_TO_EXTRACT_JWT_FROM_COOKIES: Final[str] = 'access_token_cookie=([^;]*);?'

    def __init__(self, host: str, port: int,
                 jwt_secret_key: str, jwt_algorithm: str,
                 origins: list[str],
                 ssl_context: SSLContext,
                 ) -> None:
        self._host = host
        self._port = port
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm
        self._origins = origins
        self._ssl_context = ssl_context

        self._online_set: OnlineSet = OnlineSet()
        self._signal_queue: SignalQueue = SignalQueue()
        self._clients: dict[int, list[WebSocketServerProtocol]] = {}

    def run(self) -> NoReturn:
        init_logs()  # The place chosen by experience way
        asyncio.run(self._run())

    async def _run(self) -> NoReturn:
        asyncio.create_task(self._signal_queue_pop_task())
        async with serve(ws_handler=self._handler, host=self._host, port=self._port, ssl=self._ssl_context):
            logger.info(f'WebSocketServer is serving on wss://{self._host}:{self._port}')
            await asyncio.Future()

    async def _signal_queue_pop_task(self) -> NoReturn:
        self._online_set.clear()

        message: SignalQueueMessage
        while True:
            await asyncio.sleep(0)  # For switching in the asyncio loop
            try:
                message = self._signal_queue.pop()
            except SignalQueueIsEmptyException:
                continue

            await self._send_to_many_users(
                user_ids=message.user_ids,
                message=message.message,
            )

    async def _handler(self, client: WebSocketServerProtocol) -> None:
        logger.info(f'New client connected.')
        try:
            await self._handle_client(client)
        except ConnectionClosed:
            pass
        logger.info(f'Client disconnected.')

    @raises(ConnectionClosed)
    async def _handle_client(self, client: WebSocketServerProtocol) -> None:
        if 'Cookie' not in client.request_headers:
            return

        try:
            origin: str = client.request_headers['Origin']
            cookies: str = client.request_headers['Cookie']
        except KeyError:
            return

        try:
            self._check_origin(origin)
        except InvalidOriginException:
            return

        try:
            jwt: str = self._extract_jwt_from_cookies(cookies)
        except JWTNotFoundInCookiesException:
            return

        try:
            user_id: int = self._user_id_by_jwt(jwt)
        except UserIdNotFoundInJWTException:
            return

        await self._add_client(user_id, client)
        try:
            while True:
                await client.recv()
        except ConnectionClosed:
            await self._del_client(user_id, client)
            raise

    @raises(InvalidOriginException)
    def _check_origin(self, origin: str) -> None:
        for origin_regex in self._origins:
            if re.match(origin_regex, origin):
                return
        raise InvalidOriginException

    @raises(JWTNotFoundInCookiesException)
    def _extract_jwt_from_cookies(self, cookies: str) -> str:
        match = re.search(self._RE_TO_EXTRACT_JWT_FROM_COOKIES, cookies)
        if not match:
            raise JWTNotFoundInCookiesException

        return match.group(1)

    @raises(UserIdNotFoundInJWTException)
    def _user_id_by_jwt(self, jwt: str) -> int:
        try:
            user_id: int = self._extract_user_id_from_jwt(jwt)
        except PyJWTError:
            raise UserIdNotFoundInJWTException

        db_builder.session.remove()  # For a session updating

        try:
            return User.by_id(user_id).id
        except DBEntityNotFoundException:
            raise UserIdNotFoundInJWTException

    @raises(PyJWTError)
    def _extract_user_id_from_jwt(self, jwt: str) -> int:
        try:
            decoded: dict = decode_jwt(
                jwt,
                key=self._jwt_secret_key,
                algorithms=[self._jwt_algorithm],
            )
            return int(decoded['sub'])
        except KeyError:
            raise PyJWTError

    async def _add_client(self, user_id: int,
                          client: WebSocketServerProtocol,
                          ) -> None:
        if user_id not in self._clients:
            self._clients[user_id] = []
            self._online_set.add(user_id)
            await self._send_online_statuses(user_id, True)

        self._clients[user_id].append(client)

    async def _del_client(self, user_id: int,
                          client: WebSocketServerProtocol,
                          ) -> None:
        try:
            self._clients[user_id].remove(client)
        except (KeyError, ValueError):
            return

        if not self._clients[user_id]:
            self._clients.pop(user_id)
            self._online_set.remove(user_id)
            await self._send_online_statuses(user_id, False)

    async def _send_online_statuses(self, user_id: int,
                                    status: bool,
                                    ) -> None:
        await self._send_to_many_users(
            user_ids=UserChatMatch.all_interlocutors_of_user(user_id).ids(),
            message={
                JSONKey.TYPE: SignalType.ONLINE_STATUSES,
                JSONKey.DATA: {
                    user_id: status,
                },
            },
        )

    async def _send_to_many_users(self, user_ids: list[int],
                                  message: SignalQueueMessageJSONDictToForward,
                                  ) -> None:
        user_ids = set(user_ids)
        for id_ in user_ids:
            await self._send_to_one_user(id_, message)

    async def _send_to_one_user(self, user_id: int,
                                message: SignalQueueMessageJSONDictToForward,
                                ) -> None:
        for client in self._clients.get(user_id, []):
            await self._send_to_one_client(client, message)

    @staticmethod
    async def _send_to_one_client(client: WebSocketServerProtocol,
                                  message: SignalQueueMessageJSONDictToForward,
                                  ) -> None:
        try:
            await client.send(json.dumps(message))
        except ConnectionClosed:
            return
