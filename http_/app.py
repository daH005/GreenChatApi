from traceback import print_exc

from flask import (
    Flask,
    Response,
)
from werkzeug.exceptions import HTTPException

from db.builders import db_sync_builder
from http_.app_creating import create_app
from http_.common.simple_response import make_simple_response

__all__ = (
    'app',
)

app: Flask = create_app(__name__)


@app.teardown_appcontext
def teardown_appcontext(exception: Exception | None = None) -> None:
    if exception:
        print(exception)
    db_sync_builder.session.remove()


@app.errorhandler(HTTPException)
def errorhandler(exception: HTTPException) -> Response:
    print_exc()
    return make_simple_response(exception.code)
