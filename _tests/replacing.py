from abc import ABC, abstractmethod
from typing import Any, Callable

from api.websocket_.main import server
from api.json_ import ChatMessageJSONDictMaker, ChatInfoJSONDictMaker
from api._tests.common import COMMON_DATETIME, replace_creating_datetime  # noqa
from api._tests.all_test_data.websocket_test_data import ONLINE_USERS_IDS  # noqa

__all__ = (
    'AbstractMethodReplacer',
    'ChatMessageJSONDictMakeReplacer',
    'ServerSendToOneUserMethodReplacer',
    'ServerUserHaveConnectionsMethodReplacer',
)


class AbstractMethodReplacer(ABC):
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


class ChatMessageJSONDictMakeReplacer(AbstractMethodReplacer):
    object = ChatMessageJSONDictMaker
    method_name = 'make'

    @classmethod
    def replacement_method(cls, *args, **kwargs) -> ChatMessageJSONDictMaker.Dict:
        data = cls.backup_method()(*args, **kwargs)
        replace_creating_datetime(data)
        return data


class ServerSendToOneUserMethodReplacer(AbstractMethodReplacer):
    object = server
    method_name = 'send_to_one_user'

    sendings = {}

    @classmethod
    async def replacement_method(cls, user_id: int,
                                 message: dict,
                                 ) -> None:
        cls.sendings.setdefault(user_id, []).append(message)


class ServerUserHaveConnectionsMethodReplacer(AbstractMethodReplacer):
    object = server
    method_name = 'user_have_connections'

    @staticmethod
    def replacement_method(user_id: int) -> bool:
        return user_id in ONLINE_USERS_IDS
