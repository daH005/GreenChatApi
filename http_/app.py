from traceback import format_exc, print_exc
from http import HTTPStatus

from flask import (
    Flask,
    Response,
)
from werkzeug.exceptions import HTTPException

from common.logs import logger
from db.builders import db_sync_builder
from http_.app_creating import create_app
from http_.common.simple_response import make_simple_response

__all__ = (
    'app',
)

app: Flask = create_app(__name__)


@app.teardown_appcontext
def teardown_appcontext(exception=None) -> None:
    # Very-very important: it ensures synchronization in all gunicorn workers:
    db_sync_builder.session.remove()


@app.errorhandler(HTTPException)
def errorhandler(exception: HTTPException) -> Response:
    if exception.code == HTTPStatus.INTERNAL_SERVER_ERROR:
        print_exc()
        logger.critical(format_exc())
    return make_simple_response(exception.code)
