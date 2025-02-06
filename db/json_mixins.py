from common.json_keys import JSONKey
from common.online_set import OnlineSet
from db.i import (
    IUser,
    IChat,
    IMessage,
    IUnreadCount,
    IUserList,
    IChatList,
    IMessageList,
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


class IJSONMixin:

    def as_json(self, *args, **kwargs) -> dict:
        raise NotImplementedError


class UserJSONMixin(IJSONMixin, IUser):

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


class ChatJSONMixin(IJSONMixin, IChat):

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


class MessageJSONMixin(IJSONMixin, IMessage):
    _replied_message: 'MessageJSONMixin'

    def as_json(self):
        if self._replied_message_id:
            replied_message = {
                JSONKey.ID: self._replied_message.id,
                JSONKey.USER_ID: self._replied_message.user.id,
                JSONKey.TEXT: self._replied_message.text,
            }
        else:
            replied_message = None
        return {
            JSONKey.ID: self._id,
            JSONKey.CHAT_ID: self._chat_id,
            JSONKey.USER_ID: self._user_id,
            JSONKey.TEXT: self._text,
            JSONKey.CREATING_DATETIME: self._creating_datetime.isoformat(),
            JSONKey.IS_READ: self._is_read,
            JSONKey.HAS_FILES: self.get_storage().exists(),
            JSONKey.REPLIED_MESSAGE: replied_message,
        }


class UnreadCountJSONMixin(IJSONMixin, IUnreadCount):

    def as_json(self):
        return {
            JSONKey.UNREAD_COUNT: self._value,
        }


class UserListJSONMixin(IJSONMixin, IUserList, list['UserJSONMixin']):

    def as_json(self):
        raise NotImplementedError


class ChatListJSONMixin(IJSONMixin, IChatList, list['ChatJSONMixin']):

    def as_json(self):
        return [chat.as_json(self._user_id) for chat in self]


class MessageListJSONMixin(IJSONMixin, IMessageList, list['MessageJSONMixin']):

    def as_json(self):
        return [msg.as_json() for msg in self]
