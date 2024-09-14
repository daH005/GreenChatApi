from typing import NoReturn

from config import HOST, HTTP_PORT as PORT, DEBUG
from common.ssl_context import get_ssl_context
from http_.app import app

__all__ = (
    'run_http',
)


def run_http() -> NoReturn:
    app.run(HOST, PORT, debug=DEBUG, ssl_context=get_ssl_context())
