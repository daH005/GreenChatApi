from flask import Blueprint, request, abort
from http import HTTPMethod, HTTPStatus
from pydantic import validate_email
from flasgger import swag_from

from api.common.json_ import JSONKey, CodeIsValidFlagJSONDictMaker
from api.http_.endpoints import EndpointName, Url
from api.http_.email.tasks import send_code_task
from api.http_.redis_ import make_and_save_code, code_is_valid
from api.http_.validation import EmailAndCodeJSONValidator
from api.http_.flasgger_constants import (
    SEND_CODE_SPECS,
    CHECK_CODE_SPECS,
)

__all__ = (
    'bp',
)

bp: Blueprint = Blueprint('email', __name__)


@bp.route(Url.SEND_CODE, endpoint=EndpointName.SEND_CODE, methods=[HTTPMethod.POST])
@swag_from(SEND_CODE_SPECS)
def send_code() -> dict[str, int]:
    try:
        email: str = validate_email(request.json[JSONKey.EMAIL])[1]
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        code: int = make_and_save_code(identify=email)
    except ValueError:
        raise abort(HTTPStatus.CONFLICT)
    send_code_task.delay(to=email, code=code)

    return dict(status=HTTPStatus.OK)


@bp.route(Url.CHECK_CODE, endpoint=EndpointName.CHECK_CODE, methods=[HTTPMethod.GET])
@swag_from(CHECK_CODE_SPECS)
def check_code() -> CodeIsValidFlagJSONDictMaker.Dict:
    user_data: EmailAndCodeJSONValidator = EmailAndCodeJSONValidator.from_args()

    flag: bool = code_is_valid(identify=user_data.email, code=user_data.code)
    return CodeIsValidFlagJSONDictMaker.make(flag=flag)
