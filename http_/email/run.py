from typing import NoReturn

from api.http_.email.tasks import app

__all__ = (
    'run_celery',
)


def run_celery() -> NoReturn:
    argv = [
        'worker',
        '--loglevel=INFO',
        '--pool=solo',  # Было сказано, что на Windows есть некий баг, который избегается этим параметром.
    ]
    app.worker_main(argv)
