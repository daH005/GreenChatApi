from flask import Blueprint, request, abort  # pip install flask
from http import HTTPMethod, HTTPStatus
from pydantic import validate_email  # pip install pydantic

from api.http_.endpoints import EndpointName, Url
from api.json_ import JSONKey, CodeIsValidFlagJSONDict, JSONDictPreparer
from api.http_.mail.tasks import send_code_task
from api.http_.redis_ import make_and_save_code, code_is_valid
from api.http_.funcs import make_user_identify

__all__ = (
    'bp',
)

bp: Blueprint = Blueprint('mail', __name__)


@bp.route(Url.SEND_CODE, endpoint=EndpointName.SEND_CODE, methods=[HTTPMethod.POST])
def send_code() -> dict[str, int]:
    """
    Payload JSON:
    {
        email,
    }

    Statuses - 200, 400, 409

    Returns:
    {
        status,
    }
    """
    try:
        email: str = validate_email(request.json[JSONKey.EMAIL])[1]
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        code: int = make_and_save_code(identify=make_user_identify())
    except ValueError:
        raise abort(HTTPStatus.CONFLICT)
    send_code_task.delay(to=email, code=code)

    return dict(status=HTTPStatus.OK)


@bp.route(Url.CHECK_CODE, endpoint=EndpointName.CHECK_CODE, methods=[HTTPMethod.POST])
def check_code() -> CodeIsValidFlagJSONDict:
    """
    Payload JSON:
    {
        code,
    }

    Statuses - 200, 400

    Returns:
    {
        codeIsValid,
    }
    """
    try:
        code: int = int(request.json[JSONKey.CODE])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    flag: bool = code_is_valid(identify=make_user_identify(), code=code)
    return JSONDictPreparer.prepare_code_is_valid(flag=flag)
