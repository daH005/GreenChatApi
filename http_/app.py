from traceback import format_exc

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
def teardown_appcontext(exception: HTTPException | Exception | None = None) -> None:
    if not isinstance(exception, HTTPException):
        logger.critical(format_exc())
    db_sync_builder.session.remove()


@app.errorhandler(HTTPException)
def errorhandler(exception: HTTPException) -> Response:
    return make_simple_response(exception.code)
