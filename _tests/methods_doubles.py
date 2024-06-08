from abc import ABC, abstractmethod
from typing import Any, Callable

from api.websocket_.main import server
from api.common.json_ import ChatMessageJSONDictMaker
from api._tests.common import COMMON_DATETIME
from api._tests.data.websocket_ import ONLINE_USERS_IDS

__all__ = (
    'AbstractMethodDoubleMaker',
    'ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime',
    'ServerSendToOneUserMethodDoubleMakerForServerMessagesStorage',
    'ServerUserHaveConnectionsMethodDoubleMakerForOnlineImitation',
)


class AbstractMethodDoubleMaker(ABC):
    object: object
    method_name: str

    @classmethod
    def backup_method_name(cls) -> str:
        return cls.method_name + '__backup'

    @classmethod
    def backup_method(cls) -> Callable:
        return getattr(cls.object, cls.backup_method_name())

    @classmethod
    def cur_method(cls) -> Callable:
        return getattr(cls.object, cls.method_name)

    @classmethod
    def replace(cls) -> None:
        setattr(cls.object, cls.backup_method_name(), cls.cur_method())
        setattr(cls.object, cls.method_name, cls.replacement_method)

    @classmethod
    @abstractmethod
    def replacement_method(cls, *args, **kwargs) -> Any:
        raise NotImplementedError

    @classmethod
    def back(cls) -> None:
        setattr(cls.object, cls.method_name, cls.backup_method())


class ChatMessageJSONDictMakerMakeMethodDoubleMakerForCommonDatetime(AbstractMethodDoubleMaker):
    object = ChatMessageJSONDictMaker
    method_name = 'make'

    @classmethod
    def replacement_method(cls, *args, **kwargs) -> ChatMessageJSONDictMaker.Dict:
        data = cls.backup_method()(*args, **kwargs)
        data['creatingDatetime'] = COMMON_DATETIME.isoformat()
        return data


class ServerSendToOneUserMethodDoubleMakerForServerMessagesStorage(AbstractMethodDoubleMaker):
    object = server
    method_name = 'send_to_one_user'

    saved_server_messages = {}

    @classmethod
    async def replacement_method(cls, user_id: int,
                                 message: dict,
                                 ) -> None:
        cls.saved_server_messages.setdefault(user_id, []).append(message)


class ServerUserHaveConnectionsMethodDoubleMakerForOnlineImitation(AbstractMethodDoubleMaker):
    object = server
    method_name = 'user_have_connections'

    @staticmethod
    def replacement_method(user_id: int) -> bool:
        return user_id in ONLINE_USERS_IDS
