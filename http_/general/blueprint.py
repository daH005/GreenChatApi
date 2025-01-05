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
    jwt_required,
)
from flasgger import swag_from

from db.builder import db_builder
from db.models import User, UserChatMatch, BlacklistToken
from common.json_keys import JSONKey
from http_.common.get_current_user import get_current_user
from http_.common.simple_response import make_simple_response
from http_.common.validation import EmailAndCodeJSONValidator, UserJSONValidator
from http_.email.codes.functions import (
    email_code_is_valid,
    delete_email_code,
)
from http_.common.apidocs_constants import (
    USER_EMAIL_CHECK_SPECS,
    USER_LOGIN_SPECS,
    USER_LOGOUT_SPECS,
    USER_REFRESH_ACCESS_SPECS,
    USER_INFO_SPECS,
    USER_INFO_EDIT_SPECS,
    USER_CHATS_SPECS,
    CHAT_HISTORY_SPECS,
)
from http_.common.urls import Url


__all__ = (
    'general_bp',
)

general_bp: Blueprint = Blueprint('general', __name__)


@general_bp.route(Url.USER_EMAIL_CHECK, methods=[HTTPMethod.GET])
@swag_from(USER_EMAIL_CHECK_SPECS)
def email_check():
    try:
        email: str = str(request.args[JSONKey.EMAIL])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return {
        JSONKey.IS_ALREADY_TAKEN: User.email_is_already_taken(email),
    }


@general_bp.route(Url.USER_LOGIN, methods=[HTTPMethod.POST])
@swag_from(USER_LOGIN_SPECS)
def login():
    user_data: EmailAndCodeJSONValidator = EmailAndCodeJSONValidator.from_json()

    if email_code_is_valid(user_data.email, user_data.code):
        delete_email_code(user_data.email)
    else:
        return abort(HTTPStatus.BAD_REQUEST)

    status_code: HTTPStatus
    user: User
    try:
        user = User.by_email(user_data.email)
        status_code = HTTPStatus.OK
    except ValueError:
        user = User(
            _email=user_data.email,
        )
        db_builder.session.add(user)
        db_builder.session.commit()
        status_code = HTTPStatus.CREATED

    return _make_access_response(user, status_code)


@general_bp.route(Url.USER_LOGOUT, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(USER_LOGOUT_SPECS)
def logout():
    response: Response = make_simple_response(HTTPStatus.OK)
    unset_jwt_cookies(response)
    return response


@general_bp.route(Url.USER_REFRESH_ACCESS, methods=[HTTPMethod.POST])
@jwt_required(refresh=True)
@swag_from(USER_REFRESH_ACCESS_SPECS)
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


@general_bp.route(Url.USER_INFO, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_INFO_SPECS)
def user_info():
    try:
        user_id: int = int(request.args[JSONKey.USER_ID])
    except KeyError:
        return get_current_user().as_full_json()
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    user: User | None = db_builder.session.get(User, user_id)
    if user is None:
        return abort(HTTPStatus.NOT_FOUND)

    return user.as_json()


@general_bp.route(Url.USER_INFO_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_INFO_EDIT_SPECS)
def user_info_edit():
    data: UserJSONValidator = UserJSONValidator.from_json()

    get_current_user().set_info(
        data.first_name,
        data.last_name,
    )
    db_builder.session.commit()

    return make_simple_response(HTTPStatus.OK)


@general_bp.route(Url.USER_CHATS, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_CHATS_SPECS)
def user_chats():
    return get_current_user().chats().as_json()


@general_bp.route(Url.CHAT_HISTORY, methods=[HTTPMethod.GET])
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
