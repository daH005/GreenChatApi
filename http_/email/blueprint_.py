from flask import Blueprint, request, abort  # pip install flask
from http import HTTPMethod, HTTPStatus
from pydantic import validate_email  # pip install pydantic

from api.json_ import JSONKey, CodeIsValidFlagJSONDictMaker
from api.http_.endpoints import EndpointName, Url
from api.http_.email.tasks import send_code_task
from api.http_.redis_ import make_and_save_code, code_is_valid
from api.http_.validation import EmailAndCodeJSONValidator

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

    Statuses - 200, 400, 403, 409

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
        code: int = make_and_save_code(identify=email)
    except ValueError:
        raise abort(HTTPStatus.CONFLICT)
    send_code_task.delay(to=email, code=code)

    return dict(status=HTTPStatus.OK)


@bp.route(Url.CHECK_CODE, endpoint=EndpointName.CHECK_CODE, methods=[HTTPMethod.GET])
def check_code() -> CodeIsValidFlagJSONDictMaker.Dict:
    """
    Query-params:
    - email
    - code

    Statuses - 200, 400

    Returns:
    {
        codeIsValid,
    }
    """
    user_data: EmailAndCodeJSONValidator = EmailAndCodeJSONValidator.from_args()

    flag: bool = code_is_valid(identify=user_data.email, code=user_data.code)
    return CodeIsValidFlagJSONDictMaker.make(flag=flag)
