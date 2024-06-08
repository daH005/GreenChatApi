from datetime import datetime
from typing import TypeAlias

__all__ = (
    'COMMON_DATETIME',
    'JsonDictType',
    'HeadersType',
)

COMMON_DATETIME: datetime = datetime(
    year=2024, month=10, day=10,
)

JsonDictType: TypeAlias = dict[str, str | int | bool]
HeadersType: TypeAlias = dict[str, str]
