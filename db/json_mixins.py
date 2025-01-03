from abc import abstractmethod

from common.json_keys import JSONKey

__all__ = (
    'UserJSONMixin',
    'ChatJSONMixin',
    'ChatMessageJSONMixin',
    'UserChatMatchJSONMixin',
    'UnreadCountJSONMixin',
    'ChatListJSONMixin',
    'ChatMessageListJSONMixin'
)


class AbstractJSONMixin:

    @abstractmethod
    def as_json(self, *args, **kwargs) -> dict:
        raise NotImplementedError


class UserJSONMixin(AbstractJSONMixin):

    def as_full_json(self):
        return {
            **self.as_json(),
            JSONKey.EMAIL: self._email,
        }

    def as_json(self):
        return {
            JSONKey.ID: self.id,
            JSONKey.FIRST_NAME: self._first_name,
            JSONKey.LAST_NAME: self._last_name,
        }

    @classmethod
    def email_is_already_taken_as_json(cls, email):
        return {
            JSONKey.IS_ALREADY_TAKEN: cls.email_is_already_taken(email),
        }


class ChatJSONMixin(AbstractJSONMixin):

    def as_json(self, user_id: int):
        try:
            last_message = self.last_message.as_json()
        except IndexError:
            last_message = None
        return {
            JSONKey.ID: self.id,
            JSONKey.NAME: self._name,
            JSONKey.IS_GROUP: self._is_group,
            JSONKey.LAST_CHAT_MESSAGE: last_message,
            JSONKey.USERS_IDS: [user.id for user in self.users()],
            JSONKey.UNREAD_COUNT: self.unread_count_of_user(user_id=user_id).value,
        }


class ChatMessageJSONMixin(AbstractJSONMixin):

    def as_json(self):
        return {
            JSONKey.ID: self.id,
            JSONKey.CHAT_ID: self.chat_id,
            JSONKey.TEXT: self.text,
            JSONKey.CREATING_DATETIME: self.creating_datetime.isoformat(),
            JSONKey.USER_ID: self.user_id,
            JSONKey.IS_READ: self.is_read,
            JSONKey.STORAGE_ID: self.storage_id,
        }


class UserChatMatchJSONMixin(AbstractJSONMixin):

    def as_json(self):
        pass


class UnreadCountJSONMixin(AbstractJSONMixin):

    def as_json(self):
        return {
            JSONKey.CHAT_ID: self._user_chat_match.chat_id,
            JSONKey.UNREAD_COUNT: self.value,
        }


class ChatListJSONMixin(AbstractJSONMixin):

    def as_json(self):
        return {
            JSONKey.CHATS: [chat.as_json(self._user_id) for chat in self._items]
        }


class ChatMessageListJSONMixin(AbstractJSONMixin):

    def as_json(self, offset_from_end: int = 0):
        return {
            JSONKey.MESSAGES: [msg.as_json() for msg in self._items[offset_from_end:]]
        }
