import json
from json import JSONDecodeError
from traceback import print_exc
from jwt import decode
from websockets import WebSocketServerProtocol, ConnectionClosed

from api.common.hinting import raises
from api.common.json_ import WebSocketMessageJSONDictMaker, JSONKey
from api.db.builder import DBBuilder
from api.db.models import User
from api.websocket_.base.typing_ import CommonHandlerFuncT
from api.websocket_.base.logs import logger

__all__ = (
    'WebSocketClientHandler',
)


class WebSocketClientHandler:
    _user_id: int

    def __init__(self, protocol: WebSocketServerProtocol,
                 common_handlers_funcs: dict[str, CommonHandlerFuncT],
                 jwt_secret_key: str, jwt_algorithm: str,
                 ) -> None:
        self._protocol = protocol
        self._common_handlers_funcs = common_handlers_funcs
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm

    @property
    def user(self) -> User:
        return DBBuilder.session.query(User).get(self._user_id)

    @raises(ConnectionClosed)
    async def wait_authorization(self) -> None:
        jwt: str = await self._wait_str()
        email: str = self._decode_jwt(encoded=jwt)
        try:
            self._try_to_authorize_user(email=email)
        except ValueError:
            await self.wait_authorization()

    def _decode_jwt(self, encoded: str) -> str:
        return decode(
            encoded,
            key=self._jwt_secret_key,
            algorithms=[self._jwt_algorithm],
        )['sub']

    @raises(ValueError)
    def _try_to_authorize_user(self, email: str) -> None:
        DBBuilder.session.remove()  # for session updating
        self._user_id = User.by_email(email=email).id

    @raises(ConnectionClosed)
    async def _wait_str(self) -> str:
        return await self._protocol.recv()

    @raises(ConnectionClosed, JSONDecodeError)
    async def _wait_json_dict(self) -> WebSocketMessageJSONDictMaker.Dict:
        return json.loads(await self._wait_str())

    @raises(ConnectionClosed)
    async def listen(self) -> None:
        while True:
            try:
                message: WebSocketMessageJSONDictMaker.Dict = await self._wait_json_dict()
            except JSONDecodeError:
                continue

            try:
                await self._handle_message(message)
            except Exception as e:
                msg = (f'[{self.user.id}] Handling error ({type(e).__name__}):\n'
                       f'- Message:\n'
                       f'{json.dumps(message, indent=4)}\n')
                logger.info(msg)
                print_exc()
                continue

            DBBuilder.session.remove()

    @raises(KeyError, Exception)
    async def _handle_message(self, message: WebSocketMessageJSONDictMaker.Dict) -> None:
        handler_func: CommonHandlerFuncT = self._get_handler_func(message[JSONKey.TYPE])  # type: ignore
        await handler_func(
            user=self.user,  # type: ignore
            data=message[JSONKey.DATA],  # type: ignore
        )  # type: ignore

        logger.info(f'[{self.user.id}] \"{message[JSONKey.TYPE]}\".')  # noqa

    @raises(KeyError)
    def _get_handler_func(self, type_: str) -> CommonHandlerFuncT:
        return self._common_handlers_funcs[type_]

    @raises(ConnectionClosed)
    async def send(self, message: WebSocketMessageJSONDictMaker.Dict) -> None:
        await self._protocol.send(json.dumps(message))
