from typing import Union

from db.json_mixins import (
    UserListJSONMixin,
    ChatListJSONMixin,
    MessageListJSONMixin,
)
from db.i import (
    UserListI,
    ChatListI,
    MessageListI,
)

__all__ = (
    'UserList',
    'ChatList',
    'MessageList',
)


class AbstractList(list[Union['User', 'Chat', 'Message']]):

    def ids(self) -> list[int]:
        ids = []
        for obj in self:
            ids.append(obj.id)
        return ids


class UserList(AbstractList, UserListJSONMixin, UserListI, list['User']):
    pass


class ChatList(AbstractList, ChatListJSONMixin, ChatListI, list['Chat']):

    def __init__(self, items: list['Chat'],
                 user_id: int,
                 ) -> None:
        super().__init__(items)
        self._user_id = user_id


class MessageList(AbstractList, MessageListJSONMixin, MessageListI, list['Message']):
    pass


from db.models import (
    User,  # noqa
    Chat,  # noqa
    Message,  # noqa
)
