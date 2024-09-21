from typing import NoReturn
from subprocess import run as run_subprocess

from common.ssl_context import get_ssl_context
from config import HOST, HTTP_PORT as PORT
from db.init import init_db
from http_.app import app

__all__ = (
    'run_http_with_gunicorn',
    'run_default_http',
)


def run_http_with_gunicorn() -> NoReturn:
    run_subprocess([
        'gunicorn',
        f'--certfile=ssl_/certificate.crt', f'--keyfile=ssl_/private.key',
        '-w', '4',
        '-b', f'{HOST}:{PORT}',
        'http_.app_for_wsgi:app',
    ])


def run_default_http() -> NoReturn:
    init_db()
    app.run(HOST, PORT, ssl_context=get_ssl_context())
