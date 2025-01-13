from typing import NamedTuple, TypedDict

__all__ = (
    'SignalQueueMessage',
    'SignalQueueMessageJSONDictToForward',
)


class SignalQueueMessage(NamedTuple):

    user_ids: list[int]
    message: 'SignalQueueMessageJSONDictToForward'


class SignalQueueMessageJSONDictToForward(TypedDict):

    type: str
    data: dict
