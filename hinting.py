from typing import Unpack, TypeVar, Callable

__all__ = (
    'raises',
)

func_T = TypeVar('func_T')


def raises(*exceptions: Unpack[Exception]) -> Callable[[func_T], func_T]:  # noqa
    """Декоратор для 'аннотаций' порождаемых исключений.

    @raises(ValueError, KeyError)
    def any_func():
        ...
    """
    def wrapper(func: func_T) -> func_T:
        return func
    return wrapper
