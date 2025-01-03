from db.json_mixins import (
    ChatListJSONMixin,
    ChatMessageListJSONMixin,
)


__all__ = (
    'ChatList',
    'ChatMessageList',
)


class AbstractList:

    def __init__(self, items):
        self._items = items

    def __eq__(self, other):
        if isinstance(other, list):
            return self._items == other
        return super().__eq__(other)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, item):
        return self._items[item]

    def reverse(self):
        self._items.reverse()


class ChatList(AbstractList, ChatListJSONMixin):

    def __init__(self, items, user_id):
        super().__init__(items)
        self._user_id = user_id


class ChatMessageList(AbstractList, ChatMessageListJSONMixin):
    pass
