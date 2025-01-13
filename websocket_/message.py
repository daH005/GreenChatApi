from typing import TypedDict

__all__ = (
    'WebSocketMessageJSONDict',
)


class WebSocketMessageJSONDict(TypedDict):

    type: str
    data: dict
