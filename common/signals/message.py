from typing import NamedTuple, TypedDict

from common.signals.signal_types import SignalType

__all__ = (
    'SignalQueueMessage',
    'SignalQueueMessageJSONDictToForward',
)


class SignalQueueMessage(NamedTuple):

    user_ids: list[int]
    message: 'SignalQueueMessageJSONDictToForward'


class SignalQueueMessageJSONDictToForward(TypedDict):

    type: SignalType
    data: dict
