from enum import StrEnum

__all__ = (
    'SignalType',
)


class SignalType(StrEnum):

    NEW_CHAT = 'NEW_CHAT'
    TYPING = 'TYPING'
    NEW_UNREAD_COUNT = 'NEW_UNREAD_COUNT'
    NEW_MESSAGE = 'NEW_MESSAGE'
    FILES = 'FILES'
    READ = 'READ'
    ONLINE_STATUSES = 'ONLINE_STATUSES'
