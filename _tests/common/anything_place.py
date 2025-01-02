from typing import Any

__all__ = (
    'AnythingPlace',
    'anything',
)


class AnythingPlace(str):

    def __eq__(self, other: Any) -> bool:
        return True


anything = AnythingPlace()
