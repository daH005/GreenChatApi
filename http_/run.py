from subprocess import run as run_subprocess
from typing import NoReturn

from common.ssl_context import create_ssl_context
from config import HOST, HTTP_PORT as PORT, SSL_KEYFILE, SSL_CERTFILE
from db.init import init_db
from http_.app import app

__all__ = (
    'run_http_wsgi',
    'run_default_http',
)


def run_http_wsgi() -> NoReturn:
    run_subprocess([
        'gunicorn',
        f'--certfile={SSL_CERTFILE}', f'--keyfile={SSL_KEYFILE}',
        '-w', '4',
        '-b', f'{HOST}:{PORT}',
        'http_.app_for_wsgi:app',
    ])


def run_default_http() -> NoReturn:
    init_db()
    app.run(HOST, PORT, ssl_context=create_ssl_context(SSL_CERTFILE, SSL_KEYFILE))
