from common.json_keys import JSONKey
from db.i import (
    UserI,
    ChatI,
    ChatMessageI,
    UnreadCountI,
    UserListI,
    ChatListI,
    ChatMessageListI,
)

__all__ = (
    'UserJSONMixin',
    'ChatJSONMixin',
    'ChatMessageJSONMixin',
    'UnreadCountJSONMixin',
    'UserListJSONMixin',
    'ChatListJSONMixin',
    'ChatMessageListJSONMixin'
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
        }


class ChatJSONMixin(JSONMixinI, ChatI):

    @property
    def last_message(self) -> 'ChatMessageJSONMixin':
        raise NotImplementedError

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


class ChatMessageJSONMixin(JSONMixinI, ChatMessageI):

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


class UnreadCountJSONMixin(JSONMixinI, UnreadCountI):

    def as_json(self):
        return {
            JSONKey.CHAT_ID: self._user_chat_match.chat.id,
            JSONKey.UNREAD_COUNT: self.value,
        }


class UserListJSONMixin(JSONMixinI, UserListI, list['UserJSONMixin']):

    def as_json(self):
        raise NotImplementedError


class ChatListJSONMixin(JSONMixinI, ChatListI, list['ChatJSONMixin']):

    def as_json(self):
        return {
            JSONKey.CHATS: [chat.as_json(self._user_id) for chat in self]
        }


class ChatMessageListJSONMixin(JSONMixinI, ChatMessageListI, list['ChatMessageJSONMixin']):

    def as_json(self, offset_from_end: int = 0):
        return {
            JSONKey.MESSAGES: [msg.as_json() for msg in self[offset_from_end:]]
        }
