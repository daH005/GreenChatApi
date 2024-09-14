from flask import (
    Flask,
    Response,
)
from werkzeug.exceptions import HTTPException

from db.builder import db_builder
from http_.simple_response import make_simple_response
from http_.app_preparing import prepare_app

__all__ = (
    'app',
)

app: Flask = Flask(__name__)
prepare_app(app)


@app.teardown_appcontext
def shutdown_db_session(exception=None) -> None:
    if exception:
        print(exception)
    db_builder.session.remove()


@app.errorhandler(HTTPException)
def handle_exception(exception: HTTPException) -> Response:
    return make_simple_response(exception.code)
