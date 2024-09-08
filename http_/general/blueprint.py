from flask import (
    Blueprint,
    request,
    abort,
    Response,
    jsonify,
)
from http import HTTPMethod, HTTPStatus
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    get_jwt,
    current_user,
    jwt_required,
)
from flasgger import swag_from

from api.db.builder import db_builder
from api.db.models import User, UserChatMatch, BlacklistToken
from api.common.json_ import (
    JSONKey,
    SimpleResponseStatusJSONDictMaker,
    ChatHistoryJSONDictMaker,
    UserChatsJSONDictMaker,
    UserJSONDictMaker,
    AlreadyTakenFlagJSONDictMaker,
)
from api.http_.validation import EmailAndCodeJSONValidator, UserJSONValidator
from api.http_.email.codes.functions import (
    email_code_is_valid,
    delete_email_code,
)
from api.http_.apidocs_constants import (
    EMAIL_CHECK_SPECS,
    LOGIN_SPECS,
    REFRESH_ACCESS_SPECS,
    USER_INFO_SPECS,
    USER_INFO_EDIT_SPECS,
    USER_CHATS_SPECS,
    CHAT_HISTORY_SPECS,
)
from api.http_.urls import Url

current_user: User


__all__ = (
    'bp',
)

bp: Blueprint = Blueprint('general', __name__)


@bp.route(Url.EMAIL_CHECK, methods=[HTTPMethod.GET])
@swag_from(EMAIL_CHECK_SPECS)
def email_check() -> AlreadyTakenFlagJSONDictMaker.Dict:
    try:
        email: str = str(request.args[JSONKey.EMAIL])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return AlreadyTakenFlagJSONDictMaker.make(
        flag=User.email_is_already_taken(email=email),
    )


@bp.route(Url.LOGIN, methods=[HTTPMethod.POST])
@swag_from(LOGIN_SPECS)
def login() -> tuple[Response, HTTPStatus]:
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

    response: Response = jsonify(**SimpleResponseStatusJSONDictMaker.make(status=status_code))
    set_access_cookies(response, create_access_token(identity=user.email))
    set_refresh_cookies(response, create_refresh_token(identity=user.email))

    return response, status_code


@bp.route(Url.REFRESH_ACCESS, methods=[HTTPMethod.POST])
@jwt_required(refresh=True)
@swag_from(REFRESH_ACCESS_SPECS)
def refresh_access() -> Response:
    response: Response = jsonify(**SimpleResponseStatusJSONDictMaker.make(status=HTTPStatus.OK))
    set_access_cookies(response, create_access_token(identity=current_user.email))
    set_refresh_cookies(response, create_refresh_token(identity=current_user.email))

    blacklist_token: BlacklistToken = BlacklistToken(jti=get_jwt()['jti'])
    db_builder.session.add(blacklist_token)
    db_builder.session.commit()

    return response


@bp.route(Url.USER_INFO, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_INFO_SPECS)
def user_info() -> UserJSONDictMaker.Dict:
    user_id_as_str: str | None = request.args.get(JSONKey.USER_ID)
    if user_id_as_str is None:
        return UserJSONDictMaker.make(user=current_user, exclude_important_info=False)

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
def user_info_edit() -> SimpleResponseStatusJSONDictMaker.Dict:
    data: UserJSONValidator = UserJSONValidator.from_json()

    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    db_builder.session.commit()

    return SimpleResponseStatusJSONDictMaker.make(status=HTTPStatus.OK)


@bp.route(Url.USER_CHATS, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_CHATS_SPECS)
def user_chats() -> UserChatsJSONDictMaker.Dict:
    return UserChatsJSONDictMaker.make(
        user_chats=UserChatMatch.chats_of_user(user_id=current_user.id),
        user_id=current_user.id,
    )


@bp.route(Url.CHAT_HISTORY, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_HISTORY_SPECS)
def chat_history() -> ChatHistoryJSONDictMaker.Dict:
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
        chat_messages = UserChatMatch.chat_if_user_has_access(user_id=current_user.id,
                                                              chat_id=chat_id).messages[offset_from_end:]
        return ChatHistoryJSONDictMaker.make(
            chat_messages=chat_messages,
        )
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)
