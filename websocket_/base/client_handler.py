import json
from json import JSONDecodeError
from traceback import print_exc
from jwt import decode
from websockets import WebSocketServerProtocol, ConnectionClosed

from common.hinting import raises
from websocket_.base.websocket_message import WebSocketMessageJSONDict
from common.json_keys import JSONKey
from db.builder import db_builder
from db.models import User
from websocket_.base.typing_ import CommonHandlerFuncT
from websocket_.base.logs import logger

__all__ = (
    'WebSocketClientHandler',
)


class WebSocketClientHandler:

    def __init__(self, protocol: WebSocketServerProtocol,
                 common_handlers_funcs: dict[str, CommonHandlerFuncT],
                 user_id: int,
                 ) -> None:
        self._protocol = protocol
        self._common_handlers_funcs = common_handlers_funcs
        self._user_id = user_id

    @property
    def user(self) -> User:
        return db_builder.session.query(User).get(self._user_id)

    @raises(ConnectionClosed)
    async def listen(self) -> None:
        while True:
            try:
                message: WebSocketMessageJSONDict = await self._wait_json_dict()
            except JSONDecodeError:
                continue

            try:
                await self._handle_message(message)
            except Exception as e:
                msg = (f'[{self.user.id}] Handling error ({e}):\n'
                       f'- Message:\n'
                       f'{json.dumps(message, indent=4)}\n')
                logger.info(msg)
                print_exc()
                continue

            db_builder.session.remove()

    @raises(ConnectionClosed, JSONDecodeError)
    async def _wait_json_dict(self) -> WebSocketMessageJSONDict:
        return json.loads(await self._wait_str())

    @raises(ConnectionClosed)
    async def _wait_str(self) -> str:
        return await self._protocol.recv()

    @raises(KeyError, Exception)
    async def _handle_message(self, message: WebSocketMessageJSONDict) -> None:
        handler_func: CommonHandlerFuncT = self._get_handler_func(message[JSONKey.TYPE])  # type: ignore
        await handler_func(
            user=self.user,  # type: ignore
            data=message[JSONKey.DATA],  # type: ignore
        )  # type: ignore

        logger.info(f'[{self.user.id}][{message[JSONKey.TYPE]}]')  # noqa

    @raises(KeyError)
    def _get_handler_func(self, type_: str) -> CommonHandlerFuncT:
        return self._common_handlers_funcs[type_]

    @raises(ConnectionClosed)
    async def send(self, message: WebSocketMessageJSONDict) -> None:
        await self._protocol.send(json.dumps(message))
