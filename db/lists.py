from typing import Union
from collections import UserList as CustomList

from db.i import (
    IBaseList,
    IUserList,
    IChatList,
    IMessageList,
)
from db.json_mixins import (
    UserListJSONMixin,
    ChatListJSONMixin,
    MessageListJSONMixin,
)
from db.signal_mixins import MessageListSignalMixin

__all__ = (
    'UserList',
    'ChatList',
    'MessageList',
)


class AbstractList(IBaseList, CustomList[Union['User', 'Chat', 'Message']]):

    def ids(self, exclude_ids: list[int] | None = None) -> list[int]:
        if exclude_ids is None:
            exclude_ids = []

        ids = [obj.id for obj in self]
        return [id_ for id_ in ids if id_ not in exclude_ids]


class UserList(AbstractList, UserListJSONMixin, IUserList, CustomList['User']):
    pass


class ChatList(AbstractList, ChatListJSONMixin, IChatList, CustomList['Chat']):

    def __init__(self, items: list['Chat'],
                 user_id: int,
                 ) -> None:
        super().__init__(items)
        self._user_id = user_id


class MessageList(AbstractList, MessageListJSONMixin, MessageListSignalMixin, IMessageList, CustomList['Message']):
    pass


from db.models import (  # noqa
    User,
    Chat,
    Message,
)
