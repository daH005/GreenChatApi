from flask import (
    Flask,
    request,
    abort,
    Response,
)
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from http import HTTPMethod, HTTPStatus
from json import dumps as json_dumps
from flask_jwt_extended import (
    create_access_token,
    current_user,
    jwt_required,
    JWTManager,
)
from flasgger import Swagger, swag_from

from api.db.models import User, UserChatMatch
from api.db.db_builder import DBBuilder
from api.common.json_ import (
    JSONKey,
    SimpleStatusResponseJSONDictMaker,
    ChatHistoryJSONDictMaker,
    UserChatsJSONDictMaker,
    JWTJSONDictMaker,
    UserInfoJSONDictMaker,
    AlreadyTakenFlagJSONDictMaker,
)
from api.config import (
    DEBUG,
    HOST,
    HTTP_PORT as PORT,
    CORS_ORIGINS,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES,
    DB_URL,
)
from api.http_.endpoints import EndpointName, Url
from api.http_.validation import EmailAndCodeJSONValidator, UserInfoJSONValidator
from api.http_.email.blueprint_ import (
    bp as email_bp,
)
from api.http_.avatars.blueprint_ import (
    bp as avatars_bp,
)
from api.http_.email_codes import (
    code_is_valid,
    delete_code,
)
from api.http_.apidocs_constants import (
    CHECK_EMAIL_SPECS,
    LOGIN_SPECS,
    REFRESH_TOKEN_SPECS,
    USER_INFO_SPECS,
    USER_EDIT_INFO_SPECS,
    USER_CHATS_SPECS,
    CHAT_HISTORY_SPECS,
)

current_user: User

app: Flask = Flask(__name__)
app.config.from_mapping(
    JWT_SECRET_KEY=JWT_SECRET_KEY,
    JWT_ALGORITHM=JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES=JWT_ACCESS_TOKEN_EXPIRES,
)

app.json.ensure_ascii = False

CORS(app, origins=CORS_ORIGINS)
jwt: JWTManager = JWTManager(app)

Swagger(app)

for bp in (email_bp, avatars_bp):
    app.register_blueprint(bp)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> User | None:
    email: str = jwt_data['sub']
    try:
        return User.by_email(email=email)
    except ValueError:
        return None


@app.teardown_appcontext
def shutdown_db_session(exception=None) -> None:
    if exception:
        print(exception)
    DBBuilder.session.remove()


@app.errorhandler(HTTPException)
def handle_exception(exception: HTTPException) -> Response:
    response = exception.get_response()
    response.content_type = 'application/json'
    response.data = json_dumps(dict(status=exception.code))
    return response


@app.route(Url.CHECK_EMAIL, endpoint=EndpointName.CHECK_EMAIL, methods=[HTTPMethod.GET])
@swag_from(CHECK_EMAIL_SPECS)
def check_email() -> AlreadyTakenFlagJSONDictMaker.Dict:
    try:
        email: str = str(request.args[JSONKey.EMAIL])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return AlreadyTakenFlagJSONDictMaker.make(
        flag=User.email_is_already_taken(email=email),
    )


@app.route(Url.LOGIN, endpoint=EndpointName.LOGIN, methods=[HTTPMethod.POST])
@swag_from(LOGIN_SPECS)
def login() -> tuple[JWTJSONDictMaker.Dict, HTTPStatus.OK | HTTPStatus.CREATED]:
    user_data: EmailAndCodeJSONValidator = EmailAndCodeJSONValidator.from_json()

    if code_is_valid(identify=user_data.email, code=user_data.code):
        delete_code(identify=user_data.email)
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
        DBBuilder.session.add(user)
        DBBuilder.session.commit()
        status_code = HTTPStatus.CREATED

    return JWTJSONDictMaker.make(jwt_token=create_access_token(identity=user.email)), status_code


@app.route(Url.REFRESH_TOKEN, endpoint=EndpointName.REFRESH_TOKEN, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(REFRESH_TOKEN_SPECS)
def refresh_token() -> JWTJSONDictMaker.Dict:
    return JWTJSONDictMaker.make(jwt_token=create_access_token(identity=current_user.email))


@app.route(Url.USER_INFO, endpoint=EndpointName.USER_INFO, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_INFO_SPECS)
def user_info() -> UserInfoJSONDictMaker.Dict:
    user_id_as_str: str | None = request.args.get(JSONKey.USER_ID)
    if user_id_as_str is None:
        return UserInfoJSONDictMaker.make(user=current_user, exclude_important_info=False)

    try:
        user: User | None = DBBuilder.session.get(User, int(user_id_as_str))
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    if user is None:
        return abort(HTTPStatus.NOT_FOUND)

    return UserInfoJSONDictMaker.make(user=user)


@app.route(Url.USER_EDIT_INFO, endpoint=EndpointName.USER_EDIT_INFO, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_EDIT_INFO_SPECS)
def user_edit_info() -> SimpleStatusResponseJSONDictMaker.Dict:
    data: UserInfoJSONValidator = UserInfoJSONValidator.from_json()

    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    DBBuilder.session.commit()

    return SimpleStatusResponseJSONDictMaker.make(status=HTTPStatus.OK)


@app.route(Url.USER_CHATS, endpoint=EndpointName.USER_CHATS, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_CHATS_SPECS)
def user_chats() -> UserChatsJSONDictMaker.Dict:
    return UserChatsJSONDictMaker.make(
        user_chats=UserChatMatch.chats_of_user(user_id=current_user.id),
        user_id=current_user.id,
    )


@app.route(Url.CHAT_HISTORY, endpoint=EndpointName.CHAT_HISTORY, methods=[HTTPMethod.GET])
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


if __name__ == '__main__':
    DBBuilder.init_session(url=DB_URL)
    DBBuilder.make_migrations()
    app.run(HOST, PORT, debug=DEBUG)
