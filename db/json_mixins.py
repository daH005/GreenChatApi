from common.json_keys import JSONKey
from common.online_set import OnlineSet
from db.i import (
    UserI,
    ChatI,
    MessageI,
    UnreadCountI,
    UserListI,
    ChatListI,
    MessageListI,
)

__all__ = (
    'UserJSONMixin',
    'ChatJSONMixin',
    'MessageJSONMixin',
    'UnreadCountJSONMixin',
    'UserListJSONMixin',
    'ChatListJSONMixin',
    'MessageListJSONMixin'
)


class JSONMixinI:

    def as_json(self, *args, **kwargs) -> dict:
        raise NotImplementedError


class UserJSONMixin(JSONMixinI, UserI):

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
            JSONKey.IS_ONLINE: OnlineSet().exists(self.id),
        }


class ChatJSONMixin(JSONMixinI, ChatI):

    @property
    def last_message(self) -> 'MessageJSONMixin':
        raise NotImplementedError

    def as_json(self, user_id: int):
        try:
            last_message = self.last_message.as_json()
        except IndexError:
            last_message = None

        user_ids = self.users().ids()
        interlocutor_id = None
        if not self._is_group:
            interlocutor_id = [_user_id for _user_id in user_ids if _user_id != user_id][0]

        return {
            JSONKey.ID: self._id,
            JSONKey.USER_IDS: user_ids,
            JSONKey.INTERLOCUTOR_ID: interlocutor_id,
            JSONKey.NAME: self._name,
            JSONKey.IS_GROUP: self._is_group,
            JSONKey.LAST_MESSAGE: last_message,
            JSONKey.UNREAD_COUNT: self.unread_count_of_user(user_id=user_id).value,
        }


class MessageJSONMixin(JSONMixinI, MessageI):

    def as_json(self):
        return {
            JSONKey.ID: self._id,
            JSONKey.CHAT_ID: self._chat_id,
            JSONKey.USER_ID: self._user_id,
            JSONKey.TEXT: self._text,
            JSONKey.CREATING_DATETIME: self._creating_datetime.isoformat(),
            JSONKey.IS_READ: self._is_read,
            JSONKey.HAS_FILES: self.storage.exists(),
        }


class UnreadCountJSONMixin(JSONMixinI, UnreadCountI):

    def as_json(self):
        return {
            JSONKey.UNREAD_COUNT: self._value,
        }


class UserListJSONMixin(JSONMixinI, UserListI, list['UserJSONMixin']):

    def as_json(self):
        raise NotImplementedError


class ChatListJSONMixin(JSONMixinI, ChatListI, list['ChatJSONMixin']):

    def as_json(self):
        return [chat.as_json(self._user_id) for chat in self]


class MessageListJSONMixin(JSONMixinI, MessageListI, list['MessageJSONMixin']):

    def as_json(self):
        return [msg.as_json() for msg in self]
