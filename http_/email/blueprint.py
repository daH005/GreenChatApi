from flask import Blueprint, request, abort
from http import HTTPMethod, HTTPStatus

from kombu.asynchronous.http import Response
from pydantic import validate_email
from flasgger import swag_from

from common.json_ import (
    JSONKey,
    CodeIsValidFlagJSONDictMaker,
)
from http_.simple_response import make_simple_response
from http_.urls import Url
from http_.email.tasks import send_code_task
from http_.email.codes.functions import make_and_save_email_code, email_code_is_valid
from http_.validation import EmailAndCodeJSONValidator
from http_.apidocs_constants import (
    CODE_SEND_SPECS,
    CODE_CHECK_SPECS,
)

__all__ = (
    'bp',
)

bp: Blueprint = Blueprint('email', __name__)


@bp.route(Url.CODE_SEND, methods=[HTTPMethod.POST])
@swag_from(CODE_SEND_SPECS)
def code_send() -> Response | None:
    try:
        email: str = validate_email(request.json[JSONKey.EMAIL])[1]
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        code: int = make_and_save_email_code(identify=email)
    except ValueError:
        raise abort(HTTPStatus.CONFLICT)
    send_code_task.delay(to=email, code=code)

    return make_simple_response(HTTPStatus.OK)


@bp.route(Url.CODE_CHECK, methods=[HTTPMethod.GET])
@swag_from(CODE_CHECK_SPECS)
def code_check() -> CodeIsValidFlagJSONDictMaker.Dict:
    user_data: EmailAndCodeJSONValidator = EmailAndCodeJSONValidator.from_args()

    flag: bool = email_code_is_valid(identify=user_data.email, code=user_data.code)
    return CodeIsValidFlagJSONDictMaker.make(flag=flag)
