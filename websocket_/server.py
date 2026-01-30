import json
import re
from ssl import SSLContext
from typing import NoReturn, Final
from threading import Thread

from jwt import decode as decode_jwt, PyJWTError
from websockets import ConnectionClosed
from websockets.sync.server import serve, ServerConnection

from common.hinting import raises
from common.json_keys import JSONKey
from common.online_set import OnlineSet
from common.signals.message import SignalQueueMessage, SignalQueueMessageJSONDictToForward
from common.signals.queue import SignalQueue
from common.signals.signal_types import SignalType
from common.signals.exceptions import SignalQueueIsEmptyException
from db.builders import db_sync_builder
from db.exceptions import DBEntityNotFoundException
from db.models import User, UserChatMatch
from common.logs import logger, init_logs
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
                 ssl_context: SSLContext | None = None,
                 ) -> None:
        self._host = host
        self._port = port
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm
        self._origins = origins
        self._ssl_context = ssl_context

        self._online_set: OnlineSet = OnlineSet()
        self._signal_queue: SignalQueue = SignalQueue()
        self._clients: dict[int, list[ServerConnection]] = {}

    def run(self) -> NoReturn:
        init_logs()
        Thread(target=self._signal_queue_pop_task).start()
        with serve(handler=self._handler, host=self._host, port=self._port, ssl=self._ssl_context) as server:
            logger.info(f'WebSocketServer is serving on wss://{self._host}:{self._port}')
            server.serve_forever()

    def _signal_queue_pop_task(self) -> NoReturn:
        self._online_set.clear()

        message: SignalQueueMessage
        while True:
            try:
                message = self._signal_queue.pop()
            except SignalQueueIsEmptyException:
                continue

            self._send_to_many_users(
                user_ids=message.user_ids,
                message=message.message,
            )

    def _handler(self, client: ServerConnection) -> None:
        logger.info(f'New client connected. Total connected users: {len(self._clients)}')
        try:
            self._handle_client(client)
        except ConnectionClosed:
            pass
        logger.info('Client disconnected.')

    @raises(ConnectionClosed)
    def _handle_client(self, client: ServerConnection) -> None:
        if 'Cookie' not in client.request.headers:
            return

        try:
            origin: str = client.request.headers['Origin']
            cookies: str = client.request.headers['Cookie']
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

        self._add_client(user_id, client)
        try:
            while True:
                client.recv()
        except ConnectionClosed:
            self._del_client(user_id, client)
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

        db_sync_builder.session.remove()  # For a session updating

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

    def _add_client(self, user_id: int,
                    client: ServerConnection,
                    ) -> None:
        if user_id not in self._clients:
            self._clients[user_id] = []
            self._online_set.add(user_id)
            self._send_online_statuses(user_id, True)

        self._clients[user_id].append(client)

    def _del_client(self, user_id: int,
                    client: ServerConnection,
                    ) -> None:
        try:
            self._clients[user_id].remove(client)
        except (KeyError, ValueError):
            return

        if not self._clients[user_id]:
            self._clients.pop(user_id)
            self._online_set.remove(user_id)
            self._send_online_statuses(user_id, False)

    def _send_online_statuses(self, user_id: int,
                              status: bool,
                              ) -> None:
        self._send_to_many_users(
            user_ids=UserChatMatch.all_interlocutors_of_user(user_id).ids(),
            message={
                JSONKey.TYPE: SignalType.ONLINE_STATUSES,
                JSONKey.DATA: {
                    user_id: status,
                },
            },
        )

    def _send_to_many_users(self, user_ids: list[int],
                            message: SignalQueueMessageJSONDictToForward,
                            ) -> None:
        user_ids = set(user_ids)
        for id_ in user_ids:
            self._send_to_one_user(id_, message)

    def _send_to_one_user(self, user_id: int,
                          message: SignalQueueMessageJSONDictToForward,
                          ) -> None:
        for client in self._clients.get(user_id, []):
            self._send_to_one_client(client, message)

    @staticmethod
    def _send_to_one_client(client: ServerConnection,
                            message: SignalQueueMessageJSONDictToForward,
                            ) -> None:
        try:
            client.send(json.dumps(message))
        except ConnectionClosed:
            return
