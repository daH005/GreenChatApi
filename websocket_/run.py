from typing import NoReturn

from api.websocket_.server_handlers import server

__all__ = (
    'run_websocket',
)


def run_websocket() -> NoReturn:
    server.run()
