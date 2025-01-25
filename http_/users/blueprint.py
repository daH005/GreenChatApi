from http import HTTPMethod, HTTPStatus

from flasgger import swag_from
from flask import (
    Blueprint,
    request,
    abort,
    Response,
)
from flask_jwt_extended import (
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    get_jwt,
    jwt_required,
)

from common.json_keys import JSONKey
from db.builder import db_builder
from db.models import User, BlacklistToken
from db.transaction_retry_decorator import transaction_retry_decorator
from http_.common.apidocs_constants import (
    USER_LOGIN_SPECS,
    USER_LOGOUT_SPECS,
    USER_REFRESH_ACCESS_SPECS,
    USER_SPECS,
    USER_EDIT_SPECS,
    USER_CHATS_SPECS,
)
from http_.common.get_current_user import get_current_user
from http_.common.simple_response import make_simple_response
from http_.common.urls import Url
from http_.common.validation import EmailAndCodeJSONValidator, UserJSONValidator
from http_.users.email.codes.functions import (
    email_code_is_valid,
    delete_email_code,
)
from http_.users.avatars.blueprint import avatars_bp
from http_.users.backgrounds.blueprint import backgrounds_bp
from http_.users.email.blueprint import email_bp

__all__ = (
    'users_bp',
)

users_bp: Blueprint = Blueprint('users', __name__)

for bp in (avatars_bp, backgrounds_bp, email_bp):
    users_bp.register_blueprint(bp)


@users_bp.route(Url.USER_LOGIN, methods=[HTTPMethod.POST])
@swag_from(USER_LOGIN_SPECS)
@transaction_retry_decorator()
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
        user = User.create(user_data.email)
        db_builder.session.add(user)
        db_builder.session.commit()
        status_code = HTTPStatus.CREATED

    return _make_access_response(user, status_code)


@users_bp.route(Url.USER_LOGOUT, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(USER_LOGOUT_SPECS)
def logout():
    response: Response = make_simple_response(HTTPStatus.OK)
    unset_jwt_cookies(response)
    return response


@users_bp.route(Url.USER_REFRESH_ACCESS, methods=[HTTPMethod.POST])
@jwt_required(refresh=True)
@swag_from(USER_REFRESH_ACCESS_SPECS)
@transaction_retry_decorator()
def refresh_access():
    jti: str = get_jwt()['jti']
    blacklist_token: BlacklistToken = BlacklistToken.create(jti)
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


@users_bp.route(Url.USER, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_SPECS)
def user_get():
    try:
        user_id: int = int(request.args[JSONKey.USER_ID])
    except KeyError:
        return get_current_user().as_full_json()
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        user: User = User.by_id(user_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)

    return user.as_json()


@users_bp.route(Url.USER_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_EDIT_SPECS)
@transaction_retry_decorator()
def user_edit():
    data: UserJSONValidator = UserJSONValidator.from_json()

    get_current_user().set_info(
        data.first_name,
        data.last_name,
    )
    db_builder.session.commit()

    return make_simple_response(HTTPStatus.OK)


@users_bp.route(Url.USER_CHATS, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_CHATS_SPECS)
def user_chats():
    return get_current_user().chats().as_json()
