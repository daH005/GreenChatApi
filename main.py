import pytest
from threading import Thread
from sys import argv
from typing import NoReturn

from db.alembic_.main import make_migrations
from http_.run import run_http_wsgi as run_http
from http_.users.email.run import run_celery
from websocket_.run import run_websocket


def main() -> NoReturn:
    _run_tests()

    need_migrations: bool
    try:
        if argv[1] != '--with-migrations':
            raise IndexError
        need_migrations = True
    except IndexError:
        need_migrations = False

    if need_migrations:
        make_migrations()

    for func in (run_websocket, run_http, run_celery):
        Thread(target=func).start()

    while True:
        pass


def _run_tests() -> None:
    pytest.main(['./_tests/test_http.py'])


if __name__ == '__main__':
    main()
