from http import HTTPStatus

from flask import Response, make_response

__all__ = (
    'make_simple_response',
)


def make_simple_response(status: HTTPStatus | int) -> Response:
    return make_response('', status)
