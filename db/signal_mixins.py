from common.json_keys import JSONKey
from common.signals.decorator import signal_decorator
from common.signals.signal_types import SignalType
from db.i import (
    IChat,
    IMessage,
    IMessageList,
)

__all__ = (
    'ChatSignalMixin',
    'MessageSignalMixin',
    'MessageListSignalMixin',
)


class ChatSignalMixin(IChat):

    @signal_decorator(SignalType.NEW_CHAT)
    def signal_new(self):
        return {
            JSONKey.CHAT_ID: self.id,
        }

    @signal_decorator(SignalType.TYPING)
    def signal_typing(self, user_id: int):
        return {
            JSONKey.CHAT_ID: self.id,
            JSONKey.USER_ID: user_id,
        }

    @signal_decorator(SignalType.NEW_UNREAD_COUNT)
    def signal_new_unread_count(self):
        return {
            JSONKey.CHAT_ID: self.id,
        }


class MessageSignalMixin(IMessage):

    @signal_decorator(SignalType.NEW_MESSAGE)
    def signal_new(self):
        return {
            JSONKey.CHAT_ID: self.chat.id,
            JSONKey.MESSAGE_ID: self.id,
        }

    @signal_decorator(SignalType.MESSAGE_EDIT)
    def signal_edit(self):
        return {
            JSONKey.CHAT_ID: self.chat.id,
            JSONKey.MESSAGE_ID: self.id,
        }

    @signal_decorator(SignalType.MESSAGE_DELETE)
    def signal_delete(self):
        return {
            JSONKey.CHAT_ID: self.chat.id,
            JSONKey.MESSAGE_ID: self.id,
        }

    @signal_decorator(SignalType.FILES)
    def signal_files(self):
        return {
            JSONKey.CHAT_ID: self.chat.id,
            JSONKey.MESSAGE_ID: self.id,
        }


class MessageListSignalMixin(IMessageList):

    @signal_decorator(SignalType.READ)
    def signal_read(self):
        return {
            JSONKey.CHAT_ID: self[0].chat.id,
            JSONKey.MESSAGE_IDS: self.ids(),
        }
