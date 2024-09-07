from flask import (
    Flask,
    Response,
)
from werkzeug.exceptions import HTTPException
from json import dumps as json_dumps

from api.db.builder import DBBuilder

__all__ = (
    'app',
)

app: Flask = Flask(__name__)


@app.teardown_appcontext
def shutdown_db_session(exception=None) -> None:
    if exception:
        print(exception)
    DBBuilder.session.remove()


@app.errorhandler(HTTPException)
def handle_exception(exception: HTTPException) -> Response:
    response = exception.get_response()
    response.content_type = 'application/json'
    response.data = json_dumps(dict(status=exception.code))
    return response
