from flask import (
    Blueprint,
    request,
    abort,
    Response,
)
from http import HTTPMethod, HTTPStatus
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    get_jwt,
    get_current_user,
    jwt_required,
)
from flasgger import swag_from

from db.builder import db_builder
from db.models import User, UserChatMatch, BlacklistToken
from common.json_keys import JSONKey
from http_.simple_response import make_simple_response
from http_.validation import EmailAndCodeJSONValidator, UserJSONValidator
from http_.email.codes.functions import (
    email_code_is_valid,
    delete_email_code,
)
from http_.apidocs_constants import (
    EMAIL_CHECK_SPECS,
    LOGIN_SPECS,
    LOGOUT_SPECS,
    REFRESH_ACCESS_SPECS,
    USER_INFO_SPECS,
    USER_INFO_EDIT_SPECS,
    USER_CHATS_SPECS,
    CHAT_HISTORY_SPECS,
)
from http_.urls import Url


__all__ = (
    'bp',
)

bp: Blueprint = Blueprint('general', __name__)


@bp.route(Url.EMAIL_CHECK, methods=[HTTPMethod.GET])
@swag_from(EMAIL_CHECK_SPECS)
def email_check():
    try:
        email: str = str(request.args[JSONKey.EMAIL])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return User.email_is_already_taken_as_json(email)


@bp.route(Url.LOGIN, methods=[HTTPMethod.POST])
@swag_from(LOGIN_SPECS)
def login():
    user_data: EmailAndCodeJSONValidator = EmailAndCodeJSONValidator.from_json()

    if email_code_is_valid(identify=user_data.email, code=user_data.code):
        delete_email_code(identify=user_data.email)
    else:
        return abort(HTTPStatus.BAD_REQUEST)

    status_code: HTTPStatus
    try:
        user: User = User.by_email(email=user_data.email)
        status_code = HTTPStatus.OK
    except ValueError:
        user: User = User(
            _email=user_data.email,
        )
        db_builder.session.add(user)
        db_builder.session.commit()
        status_code = HTTPStatus.CREATED

    return _make_access_response(user, status_code)


@bp.route(Url.LOGOUT, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(LOGOUT_SPECS)
def logout():
    response: Response = make_simple_response(HTTPStatus.OK)
    unset_jwt_cookies(response)

    return response


@bp.route(Url.REFRESH_ACCESS, methods=[HTTPMethod.POST])
@jwt_required(refresh=True)
@swag_from(REFRESH_ACCESS_SPECS)
def refresh_access():
    blacklist_token: BlacklistToken = BlacklistToken(_jti=get_jwt()['jti'])
    db_builder.session.add(blacklist_token)
    db_builder.session.commit()

    return _make_access_response(get_current_user(), HTTPStatus.OK)


def _make_access_response(user: User,
                          status_code: HTTPStatus | int,
                          ) -> Response:
    response: Response = make_simple_response(status_code)
    set_access_cookies(response, user.create_access_token())
    set_refresh_cookies(response, user.create_refresh_token())

    return response


@bp.route(Url.USER_INFO, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_INFO_SPECS)
def user_info():
    user_id_as_str: str | None = request.args.get(JSONKey.USER_ID)
    if user_id_as_str is None:
        return get_current_user().as_full_json()

    try:
        user: User | None = db_builder.session.get(User, int(user_id_as_str))
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    if user is None:
        return abort(HTTPStatus.NOT_FOUND)

    return user.as_json()


@bp.route(Url.USER_INFO_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_INFO_EDIT_SPECS)
def user_info_edit():
    data: UserJSONValidator = UserJSONValidator.from_json()

    get_current_user().set_info(
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db_builder.session.commit()

    return make_simple_response(HTTPStatus.OK)


@bp.route(Url.USER_CHATS, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_CHATS_SPECS)
def user_chats():
    return get_current_user().chats().as_json()


@bp.route(Url.CHAT_HISTORY, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_HISTORY_SPECS)
def chat_history():
    try:
        chat_id: int = int(request.args[JSONKey.CHAT_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    offset_from_end: int | None
    try:
        offset_from_end = int(request.args[JSONKey.OFFSET_FROM_END])
        if offset_from_end < 0:
            raise ValueError
    except KeyError:
        offset_from_end = None
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        return UserChatMatch.chat_if_user_has_access(get_current_user().id, chat_id).messages().as_json(offset_from_end)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)
