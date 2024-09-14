from typing import NoReturn
from subprocess import run as run_subprocess

from config import HOST, HTTP_PORT as PORT

__all__ = (
    'run_http',
)


def run_http() -> NoReturn:
    run_subprocess([
        'gunicorn',
        f'--certfile=ssl_/certificate.crt', f'--keyfile=ssl_/private.key',
        '-w', '4',
        '-b', f'{HOST}:{PORT}',
        'http_.app_for_wsgi:app',
    ])
