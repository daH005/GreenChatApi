from abc import ABC, abstractmethod
from typing import Any

from api.http_.main import app
from api.websocket_.main import server
from api.common.json_ import ChatMessageJSONDictMaker
from api._tests.common import COMMON_DATETIME
from api._tests.data.websocket_ import ONLINE_USERS_IDS

__all__ = (
    'AbstractDoubleMaker',
    'ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime',
    'WebsocketServerSendToOneUserMethodDoubleMakerForServerMessagesStorage',
    'WebsocketServerUserHaveConnectionsMethodDoubleMakerForOnlineImitation',
    'HttpAppTeardownContextFunctionsListDoubleMakerForNoSessionConflictException',
)


class AbstractDoubleMaker(ABC):
    object: object
    attr_name: str

    @classmethod
    def backup_attr_name(cls) -> str:
        return cls.attr_name + '__backup'

    @classmethod
    def backup_attr(cls) -> Any:
        return getattr(cls.object, cls.backup_attr_name())

    @classmethod
    def cur_attr(cls) -> Any:
        return getattr(cls.object, cls.attr_name)

    @classmethod
    def replace(cls) -> None:
        setattr(cls.object, cls.backup_attr_name(), cls.cur_attr())
        setattr(cls.object, cls.attr_name, cls.replacement_attr)

    @classmethod
    @abstractmethod
    def replacement_attr(cls, *args, **kwargs) -> Any:
        raise NotImplementedError

    @classmethod
    def back(cls) -> None:
        setattr(cls.object, cls.attr_name, cls.backup_attr())


class ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime(AbstractDoubleMaker):
    object = ChatMessageJSONDictMaker
    attr_name = 'make'

    @classmethod
    def replacement_attr(cls, *args, **kwargs) -> ChatMessageJSONDictMaker.Dict:
        data = cls.backup_attr()(*args, **kwargs)
        data['creatingDatetime'] = COMMON_DATETIME.isoformat()
        return data


class WebsocketServerSendToOneUserMethodDoubleMakerForServerMessagesStorage(AbstractDoubleMaker):
    object = server
    attr_name = 'send_to_one_user'

    saved_server_messages = {}

    @classmethod
    async def replacement_attr(cls, user_id: int,
                               message: dict,
                               ) -> None:
        cls.saved_server_messages.setdefault(user_id, []).append(message)


class WebsocketServerUserHaveConnectionsMethodDoubleMakerForOnlineImitation(AbstractDoubleMaker):
    object = server
    attr_name = 'user_have_connections'

    @staticmethod
    def replacement_attr(user_id: int) -> bool:
        return user_id in ONLINE_USERS_IDS


class HttpAppTeardownContextFunctionsListDoubleMakerForNoSessionConflictException(AbstractDoubleMaker):
    object = app
    attr_name = 'teardown_appcontext_funcs'
    replacement_attr = []
