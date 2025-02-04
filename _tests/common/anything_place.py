from typing import Any

__all__ = (
    'AnythingPlace',
    'anything_place',
)


class AnythingPlace(str):

    def __eq__(self, other: Any) -> bool:
        return True


anything_place: AnythingPlace = AnythingPlace()
