from typing import NoReturn

from common.ssl_context import create_ssl_context
from config import (
    HOST,
    WEBSOCKET_PORT,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    CORS_ORIGINS,
    SSL_CERTFILE,
    SSL_KEYFILE,
)
from db.init import init_db
from websocket_.server import WebSocketServer

__all__ = (
    'run_websocket',
)


def run_websocket() -> NoReturn:
    init_db()
    server: WebSocketServer = WebSocketServer(
        host=HOST,
        port=WEBSOCKET_PORT,
        jwt_secret_key=JWT_SECRET_KEY,
        jwt_algorithm=JWT_ALGORITHM,
        origins=CORS_ORIGINS,
        ssl_context=create_ssl_context(SSL_CERTFILE, SSL_KEYFILE),
    )
    server.run()
