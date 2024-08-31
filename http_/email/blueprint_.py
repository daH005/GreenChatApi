from flask import Blueprint, request, abort
from http import HTTPMethod, HTTPStatus
from pydantic import validate_email
from flasgger import swag_from

from api.common.json_ import (
    JSONKey,
    CodeIsValidFlagJSONDictMaker,
    SimpleResponseStatusJSONDictMaker,
)
from api.http_.urls import Url
from api.http_.email.tasks import send_code_task
from api.http_.email.codes import make_and_save_email_code, email_code_is_valid
from api.http_.validation import EmailAndCodeJSONValidator
from api.http_.apidocs_constants import (
    CODE_SEND_SPECS,
    CODE_CHECK_SPECS,
)

__all__ = (
    'bp',
)

bp: Blueprint = Blueprint('email', __name__)


@bp.route(Url.CODE_SEND, methods=[HTTPMethod.POST])
@swag_from(CODE_SEND_SPECS)
def code_send() -> SimpleResponseStatusJSONDictMaker.Dict:
    try:
        email: str = validate_email(request.json[JSONKey.EMAIL])[1]
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        code: int = make_and_save_email_code(identify=email)
    except ValueError:
        raise abort(HTTPStatus.CONFLICT)
    send_code_task.delay(to=email, code=code)

    return SimpleResponseStatusJSONDictMaker.make(status=HTTPStatus.OK)


@bp.route(Url.CODE_CHECK, methods=[HTTPMethod.GET])
@swag_from(CODE_CHECK_SPECS)
def code_check() -> CodeIsValidFlagJSONDictMaker.Dict:
    user_data: EmailAndCodeJSONValidator = EmailAndCodeJSONValidator.from_args()

    flag: bool = email_code_is_valid(identify=user_data.email, code=user_data.code)
    return CodeIsValidFlagJSONDictMaker.make(flag=flag)
