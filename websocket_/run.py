from typing import NoReturn

from db.init import init_db
from websocket_.server_handlers import server

__all__ = (
    'run_websocket',
)


def run_websocket() -> NoReturn:
    init_db()
    server.run()
