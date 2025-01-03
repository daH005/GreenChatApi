from abc import abstractmethod
from datetime import datetime

from common.json_keys import JSONKey

__all__ = (
    'UserJSONMixin',
    'ChatJSONMixin',
    'ChatMessageJSONMixin',
    'UnreadCountJSONMixin',
    'ChatListJSONMixin',
    'ChatMessageListJSONMixin'
)


class AbstractJSONMixin:

    @abstractmethod
    def as_json(self, *args, **kwargs) -> dict:
        raise NotImplementedError


class UserJSONMixin(AbstractJSONMixin):

    id: int
    _id: int
    _email: str
    _first_name: str
    _last_name: str

    def as_full_json(self):
        return {
            **self.as_json(),
            JSONKey.EMAIL: self._email,
        }

    def as_json(self):
        return {
            JSONKey.ID: self._id,
            JSONKey.FIRST_NAME: self._first_name,
            JSONKey.LAST_NAME: self._last_name,
        }

    @classmethod
    def email_is_already_taken_as_json(cls, email):
        return {
            JSONKey.IS_ALREADY_TAKEN: cls.email_is_already_taken(email),
        }

    @classmethod
    def email_is_already_taken(cls, email: str) -> bool:
        raise NotImplementedError


class ChatJSONMixin(AbstractJSONMixin):

    _id: int
    _name: str | None
    _is_group: bool
    last_message: 'ChatMessageJSONMixin'

    def as_json(self, user_id: int):
        try:
            last_message = self.last_message.as_json()
        except IndexError:
            last_message = None
        return {
            JSONKey.ID: self._id,
            JSONKey.NAME: self._name,
            JSONKey.IS_GROUP: self._is_group,
            JSONKey.LAST_CHAT_MESSAGE: last_message,
            JSONKey.USER_IDS: [user.id for user in self.users()],
            JSONKey.UNREAD_COUNT: self.unread_count_of_user(user_id=user_id).value,
        }

    def users(self) -> list['UserJSONMixin']:
        raise NotImplementedError

    def unread_count_of_user(self, user_id: int) -> 'UnreadCountJSONMixin':
        raise NotImplementedError


class ChatMessageJSONMixin(AbstractJSONMixin):

    _id: int
    _chat_id: int
    _user_id: int
    _text: str
    _creating_datetime: datetime
    _is_read: bool
    _storage_id: int | None

    def as_json(self):
        return {
            JSONKey.ID: self._id,
            JSONKey.CHAT_ID: self._chat_id,
            JSONKey.USER_ID: self._user_id,
            JSONKey.TEXT: self._text,
            JSONKey.CREATING_DATETIME: self._creating_datetime.isoformat(),
            JSONKey.IS_READ: self._is_read,
            JSONKey.STORAGE_ID: self._storage_id,
        }


class UnreadCountJSONMixin(AbstractJSONMixin):

    value: int
    _user_chat_match: object

    def as_json(self):
        return {
            JSONKey.CHAT_ID: self._user_chat_match._chat_id,
            JSONKey.UNREAD_COUNT: self.value,
        }


class ChatListJSONMixin(AbstractJSONMixin):

    _user_id: int
    _items: list['ChatJSONMixin']

    def as_json(self):
        return {
            JSONKey.CHATS: [chat.as_json(self._user_id) for chat in self._items]
        }


class ChatMessageListJSONMixin(AbstractJSONMixin):

    _items: list['ChatMessageJSONMixin']

    def as_json(self, offset_from_end: int = 0):
        return {
            JSONKey.MESSAGES: [msg.as_json() for msg in self._items[offset_from_end:]]
        }
