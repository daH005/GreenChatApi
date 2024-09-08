from typing import NoReturn

from api.config import HOST, HTTP_PORT as PORT, DEBUG
from api.common.ssl_context import get_ssl_context
from api.http_.app import app
from api.http_.app_preparing import init_all_dependencies

__all__ = (
    'run_http',
)


def run_http() -> NoReturn:
    init_all_dependencies()
    app.run(HOST, PORT, debug=DEBUG, ssl_context=get_ssl_context())
