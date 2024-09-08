from typing import Callable, Coroutine

from db.models import User

__all__ = (
    'CommonHandlerFuncT',
    'ConnectAndDisconnectHandlerFuncT',
)

CommonHandlerFuncT = Callable[[User, dict], Coroutine]
ConnectAndDisconnectHandlerFuncT = Callable[[User], Coroutine]
