from flask import Flask, request, abort, Response  # pip install flask
from werkzeug.exceptions import HTTPException
from flask_cors import CORS  # pip install -U flask-cors
from http import HTTPMethod, HTTPStatus
from json import dumps as json_dumps
from flask_jwt_extended import (  # pip install flask-jwt-extended
    create_access_token,
    current_user,
    jwt_required,
    JWTManager,
)

from api.db.models import User, UserChatMatch, session
from api.json_ import (
    ChatHistoryJSONDict,
    UserChatsJSONDict,
    JWTTokenJSONDict,
    UserInfoJSONDict,
    AlreadyTakenFlagJSONDict,
    JSONKey,
    JSONDictPreparer,
)
from api.config import (
    DEBUG,
    HOST,
    HTTP_PORT as PORT,
    CORS_ORIGINS,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES,
)
from endpoints import EndpointName, Url
from validation import UserJSONValidator
from api.http_.mail.blueprint_ import (
    bp as mail_bp,
)
from api.http_.redis_ import (
    code_is_valid,
    delete_code,
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

app.register_blueprint(mail_bp)


@jwt.user_identity_loader
def user_identity_lookup(user: User) -> str:
    return user.auth_token


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> User | None:
    identity: str = jwt_data['sub']
    try:
        return User.auth_by_token(auth_token=identity)
    except ValueError:
        return None


@app.teardown_appcontext
def shutdown_db_session(exception=None) -> None:
    if exception:
        print(exception)
    session.remove()


@app.errorhandler(HTTPException)
def handle_exception(exception: HTTPException) -> Response:
    response = exception.get_response()
    response.content_type = 'application/json'
    response.data = json_dumps(dict(status=exception.code))
    return response


@app.route(Url.REG, endpoint=EndpointName.REG, methods=[HTTPMethod.POST])
def create_new_user() -> tuple[JWTTokenJSONDict, HTTPStatus.CREATED]:
    """
    Payload JSON:
    {
        username,
        password,
        firstName,
        lastName,
        email,
        code
    }

    Statuses - 201, 400, 409

    Returns:
    {
        JWTToken,
    }
    """
    user_data: UserJSONValidator = UserJSONValidator.from_json()

    if code_is_valid(user_data.code):
        delete_code(user_data.code)
    else:
        return abort(HTTPStatus.BAD_REQUEST)

    if User.username_is_already_taken(username_to_check=user_data.username):
        return abort(HTTPStatus.CONFLICT)
    if User.email_is_already_taken(email_to_check=user_data.email):
        return abort(HTTPStatus.CONFLICT)

    new_user: User = User.new_by_password(
        username=user_data.username,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
    )
    session.add(new_user)
    session.commit()

    return JSONDictPreparer.prepare_jwt_token(jwt_token=create_access_token(identity=new_user)), HTTPStatus.CREATED


@app.route(Url.CHECK_USERNAME, endpoint=EndpointName.CHECK_USERNAME, methods=[HTTPMethod.GET])
def check_username() -> AlreadyTakenFlagJSONDict:
    """
    Query-params:
    - username

    Statuses - 200, 400

    Returns:
    {
        isAlreadyTaken,
    }
    """
    try:
        username: str = str(request.args[JSONKey.USERNAME])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return JSONDictPreparer.prepare_already_taken(
        flag=User.username_is_already_taken(username_to_check=username),
    )


@app.route(Url.CHECK_EMAIL, endpoint=EndpointName.CHECK_EMAIL, methods=[HTTPMethod.GET])
def check_email() -> AlreadyTakenFlagJSONDict:
    """
    Query-params:
    - email

    Statuses - 200, 400

    Returns:
    {
        isAlreadyTaken,
    }
    """
    try:
        email: str = str(request.args[JSONKey.EMAIL])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return JSONDictPreparer.prepare_already_taken(
        flag=User.email_is_already_taken(email_to_check=email),
    )


@app.route(Url.AUTH, endpoint=EndpointName.AUTH, methods=[HTTPMethod.POST])
def auth_by_username_and_password() -> JWTTokenJSONDict:
    """
    Payload JSON:
    {
        username,
        password,
    }

    Statuses - 201, 400, 403

    Returns:
    {
        JWTToken,
    }
    """
    try:
        username: str = str(request.json[JSONKey.USERNAME])
        password: str = str(request.json[JSONKey.PASSWORD])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        auth_user: User = User.auth_by_username_and_password(username, password)
    except ValueError:
        return abort(HTTPStatus.FORBIDDEN)

    return JSONDictPreparer.prepare_jwt_token(jwt_token=create_access_token(identity=auth_user))


@app.route(Url.REFRESH_TOKEN, endpoint=EndpointName.REFRESH_TOKEN, methods=[HTTPMethod.POST])
@jwt_required()
def refresh_token() -> JWTTokenJSONDict:
    """
    Headers:
    Authorization: Bearer <JWT-Token>

    Payload JSON:
    {
        username,
        password,
    }

    Statuses - 200, 401

    Returns:
    {
        JWTToken,
    }
    """
    return JSONDictPreparer.prepare_jwt_token(jwt_token=create_access_token(identity=current_user))


@app.route(Url.USER_INFO, endpoint=EndpointName.USER_INFO, methods=[HTTPMethod.GET])
@jwt_required()
def user_info() -> UserInfoJSONDict:
    """
    Headers:
    Authorization: Bearer <JWT-Token>

    Query-params:
    - id

    Statuses - 200, 400, 401, 404

    Returns:
    {
        id,
        firstName,
        lastName,
        ?email,
        ?username,
    }
    """
    user_id_as_str: str | None = request.args.get(JSONKey.ID)
    if user_id_as_str is None:
        return JSONDictPreparer.prepare_user_info(user=current_user, exclude_important_info=False)

    try:
        user: User | None = session.get(User, int(user_id_as_str))
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    if user is None:
        return abort(HTTPStatus.NOT_FOUND)

    return JSONDictPreparer.prepare_user_info(user=user)


@app.route(Url.USER_CHATS, endpoint=EndpointName.USER_CHATS, methods=[HTTPMethod.GET])
@jwt_required()
def user_chats() -> UserChatsJSONDict:
    """ Чаты отсортированы по `ChatMessage.creating_datetime` (первый - поздний).

    Headers:
    Authorization: Bearer <JWT-Token>

    Statuses - 200, 401

    Returns:
    {
        chats: [
            {
                id,
                name,
                isGroup,
                users: [
                    {
                        id,
                        firstName,
                        lastName,
                    },
                    ...
                ],
                lastMessage: {
                    id,
                    chatId,
                    text,
                    creatingDatetime,
                    user: {
                        id,
                        firstName,
                        lastName,
                    },
                }
            },
            ...
        ],
    }
    """
    return JSONDictPreparer.prepare_user_chats(
        user_chats=UserChatMatch.user_chats(user_id=current_user.id),
    )


@app.route(Url.CHAT_HISTORY, endpoint=EndpointName.CHAT_HISTORY, methods=[HTTPMethod.GET])
@jwt_required()
def chat_history(chat_id: int) -> ChatHistoryJSONDict:
    """Сообщения отсортированы по `ChatMessage.creating_datetime` (первое - позднее).

    Headers:
    Authorization: Bearer <JWT-Token>

    Query-params:
    - offsetFromEnd (optional)

    Statuses - 200, 400, 401, 403

    Returns:
    {
        messages: [
            {
                id,
                chatId,
                text,
                creatingDatetime,
                user: {
                    id,
                    firstName,
                    lastName,
                },
            },
            ...
        ],
    }
    """
    offset_from_end: int | None
    try:
        offset_from_end = -int(request.args[JSONKey.OFFSET_FROM_END])
    except KeyError:
        offset_from_end = None
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        chat_messages = UserChatMatch.chat_if_user_has_access(user_id=current_user.id,
                                                              chat_id=chat_id).messages[:offset_from_end]
        chat_messages = sorted(chat_messages, key=lambda x: -x.creating_datetime.timestamp())
        return JSONDictPreparer.prepare_chat_history(
            chat_messages=chat_messages,
        )
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)


if __name__ == '__main__':
    app.run(HOST, PORT, debug=DEBUG)
