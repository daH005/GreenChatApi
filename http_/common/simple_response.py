from flask import Response, make_response
from http import HTTPStatus

__all__ = (
    'make_simple_response',
)


def make_simple_response(status: HTTPStatus | int) -> Response:
    return make_response('', status)
