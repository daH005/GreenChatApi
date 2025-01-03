from typing import Unpack, TypeVar, Callable

__all__ = (
    'raises',
)

FuncT = TypeVar('FuncT')


def raises(*_exceptions: Unpack[Exception]) -> Callable[[FuncT], FuncT]:
    def wrapper(func: FuncT) -> FuncT:
        return func
    return wrapper
