from http import HTTPMethod, HTTPStatus

from flasgger import swag_from
from flask import Blueprint, request, abort
from pydantic import validate_email

from common.json_keys import JSONKey
from http_.common.apidocs_constants import (
    USER_EMAIL_CODE_SEND_SPECS,
    USER_EMAIL_CODE_CHECK_SPECS,
)
from http_.common.simple_response import make_simple_response
from http_.common.urls import Url
from http_.common.validation import EmailAndCodeJSONValidator
from http_.email.codes.functions import make_and_save_email_code, email_code_is_valid
from http_.email.tasks import send_code_task

__all__ = (
    'email_bp',
)

email_bp: Blueprint = Blueprint('email', __name__)


@email_bp.route(Url.USER_CODE_SEND, methods=[HTTPMethod.POST])
@swag_from(USER_EMAIL_CODE_SEND_SPECS)
def code_send():
    try:
        email: str = validate_email(request.json[JSONKey.EMAIL])[1]
    except (KeyError, ValueError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        code: int = make_and_save_email_code(email)
    except ValueError:
        return abort(HTTPStatus.CONFLICT)
    send_code_task.delay(to=email, code=code)

    return make_simple_response(HTTPStatus.ACCEPTED)


@email_bp.route(Url.USER_CODE_CHECK, methods=[HTTPMethod.GET])
@swag_from(USER_EMAIL_CODE_CHECK_SPECS)
def code_check():
    user_data: EmailAndCodeJSONValidator = EmailAndCodeJSONValidator.from_args()
    return {
        JSONKey.CODE_IS_VALID: email_code_is_valid(user_data.email, user_data.code),
    }
