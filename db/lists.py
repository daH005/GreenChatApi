from typing import Union

from db.json_mixins import (
    UserListJSONMixin,
    ChatListJSONMixin,
    ChatMessageListJSONMixin,
)
from db.i import (
    UserListI,
    ChatListI,
    ChatMessageListI,
)

__all__ = (
    'UserList',
    'ChatList',
    'ChatMessageList',
)


class AbstractList(list[Union['User', 'Chat', 'ChatMessage']]):

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


class ChatMessageList(AbstractList, ChatMessageListJSONMixin, ChatMessageListI, list['ChatMessage']):
    pass


from db.models import (
    User,  # noqa
    Chat,  # noqa
    ChatMessage,  # noqa
)
