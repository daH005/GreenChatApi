from typing import Union

from db.i import (
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


class AbstractList(list[Union['User', 'Chat', 'Message']]):

    def ids(self, exclude_ids: list[int] | None = None) -> list[int]:
        if exclude_ids is None:
            exclude_ids = []
        return list(filter(lambda x: x not in exclude_ids, map(lambda x: x.id, self)))


class UserList(AbstractList, UserListJSONMixin, IUserList, list['User']):
    pass


class ChatList(AbstractList, ChatListJSONMixin, IChatList, list['Chat']):

    def __init__(self, items: list['Chat'],
                 user_id: int,
                 ) -> None:
        super().__init__(items)
        self._user_id = user_id


class MessageList(AbstractList, MessageListJSONMixin, MessageListSignalMixin, IMessageList, list['Message']):
    pass


from db.models import (  # noqa
    User,
    Chat,
    Message,
)
