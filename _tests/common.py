from datetime import datetime
from typing import TypeAlias

__all__ = (
    'COMMON_DATETIME',
    'JsonDictType',
    'HeadersOrQueryArgsType',
)

COMMON_DATETIME: datetime = datetime(
    year=2024, month=10, day=10,
)

JsonDictType: TypeAlias = dict[str, str | int | bool]
HeadersOrQueryArgsType: TypeAlias = dict[str, str]
