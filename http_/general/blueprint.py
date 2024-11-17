from line_profiler import profile
from flask import (
    Blueprint,
    request,
    abort,
    Response,
)
from http import HTTPMethod, HTTPStatus
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
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
from common.json_ import (
    JSONKey,
    ChatHistoryJSONDictMaker,
    UserChatsJSONDictMaker,
    UserJSONDictMaker,
    AlreadyTakenFlagJSONDictMaker,
)
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
@profile
def email_check() -> AlreadyTakenFlagJSONDictMaker.Dict | None:
    try:
        email: str = str(request.args[JSONKey.EMAIL])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return AlreadyTakenFlagJSONDictMaker.make(
        flag=User.email_is_already_taken(email=email),
    )


@bp.route(Url.LOGIN, methods=[HTTPMethod.POST])
@swag_from(LOGIN_SPECS)
@profile
def login() -> Response | None:
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
            email=user_data.email,
        )
        db_builder.session.add(user)
        db_builder.session.commit()
        status_code = HTTPStatus.CREATED

    response: Response = make_simple_response(status_code)
    set_access_cookies(response, create_access_token(identity=user.email))
    set_refresh_cookies(response, create_refresh_token(identity=user.email))

    return response


@bp.route(Url.LOGOUT, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(LOGOUT_SPECS)
@profile
def logout() -> Response:
    response: Response = make_simple_response(HTTPStatus.OK)
    unset_jwt_cookies(response)

    return response


@bp.route(Url.REFRESH_ACCESS, methods=[HTTPMethod.POST])
@jwt_required(refresh=True)
@swag_from(REFRESH_ACCESS_SPECS)
@profile
def refresh_access() -> Response:
    response: Response = make_simple_response(HTTPStatus.OK)

    current_user: User = get_current_user()
    set_access_cookies(response, create_access_token(identity=current_user.email))
    set_refresh_cookies(response, create_refresh_token(identity=current_user.email))

    blacklist_token: BlacklistToken = BlacklistToken(jti=get_jwt()['jti'])
    db_builder.session.add(blacklist_token)
    db_builder.session.commit()

    return response


@bp.route(Url.USER_INFO, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_INFO_SPECS)
@profile
def user_info() -> UserJSONDictMaker.Dict | None:
    user_id_as_str: str | None = request.args.get(JSONKey.USER_ID)
    if user_id_as_str is None:
        return UserJSONDictMaker.make(user=get_current_user(), exclude_important_info=False)

    try:
        user: User | None = db_builder.session.get(User, int(user_id_as_str))
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    if user is None:
        return abort(HTTPStatus.NOT_FOUND)

    return UserJSONDictMaker.make(user=user)


@bp.route(Url.USER_INFO_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_INFO_EDIT_SPECS)
@profile
def user_info_edit() -> Response:
    data: UserJSONValidator = UserJSONValidator.from_json()

    current_user: User = get_current_user()
    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    db_builder.session.commit()

    return make_simple_response(HTTPStatus.OK)


@bp.route(Url.USER_CHATS, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_CHATS_SPECS)
@profile
def user_chats() -> UserChatsJSONDictMaker.Dict:
    current_user: User = get_current_user()
    return UserChatsJSONDictMaker.make(
        user_chats=UserChatMatch.chats_of_user(user_id=current_user.id),
        user_id=current_user.id,
    )


@bp.route(Url.CHAT_HISTORY, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_HISTORY_SPECS)
@profile
def chat_history() -> ChatHistoryJSONDictMaker.Dict | None:
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
        chat_messages = UserChatMatch.chat_if_user_has_access(user_id=get_current_user().id,
                                                              chat_id=chat_id).messages[offset_from_end:]
        return ChatHistoryJSONDictMaker.make(
            chat_messages=chat_messages,
        )
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)
