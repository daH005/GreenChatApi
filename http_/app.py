from flask import (
    Flask,
    Response,
)
from werkzeug.exceptions import HTTPException

from db.builder import db_builder
from http_.simple_response import make_simple_response
from http_.app_creating import create_app

__all__ = (
    'app',
)

app: Flask = create_app(__name__)


@app.teardown_appcontext
def shutdown_db_session(exception=None) -> None:
    if exception:
        print(exception)
    db_builder.session.remove()


@app.errorhandler(HTTPException)
def handle_exception(exception: HTTPException) -> Response:
    return make_simple_response(exception.code)
