from typing import NoReturn

from http_.users.email.tasks import app

__all__ = (
    'run_celery',
)


def run_celery() -> NoReturn:
    argv = [
        'worker',
        '--loglevel=INFO',
    ]
    app.worker_main(argv)
