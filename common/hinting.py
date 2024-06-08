from typing import Unpack, TypeVar, Callable

__all__ = (
    'raises',
)

func_T = TypeVar('func_T')


def raises(*_exceptions: Unpack[Exception]) -> Callable[[func_T], func_T]:
    """Decorator for annotation of exceptions.

    @raises(ValueError, KeyError)
    def any_func():
        ...
    """
    def wrapper(func: func_T) -> func_T:
        return func
    return wrapper
