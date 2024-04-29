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

from api.db.models import User, UserChatMatch, DBBuilder
from api.json_ import (
    JSONKey,
    ChatHistoryJSONDictMaker,
    UserChatsJSONDictMaker,
    JWTTokenJSONDictMaker,
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
from endpoints import EndpointName, Url
from validation import EmailAndCodeJSONValidator
from api.http_.email.blueprint_ import (
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


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> User | None:
    email: str = jwt_data['sub']
    try:
        return User.find_by_email(email=email)
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
def check_email() -> AlreadyTakenFlagJSONDictMaker.Dict:
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

    return AlreadyTakenFlagJSONDictMaker.make(
        flag=User.email_is_already_taken(email=email),
    )


@app.route(Url.AUTH, endpoint=EndpointName.AUTH, methods=[HTTPMethod.POST])
def auth() -> tuple[JWTTokenJSONDictMaker.Dict, HTTPStatus.OK | HTTPStatus.CREATED]:
    """
    Payload JSON:
    {
        email,
        code
    }

    Statuses - 200, 201, 400

    Returns:
    {
        JWTToken,
    }
    """
    user_data: EmailAndCodeJSONValidator = EmailAndCodeJSONValidator.from_json()

    if code_is_valid(identify=user_data.email, code=user_data.code):
        delete_code(identify=user_data.email)
    else:
        return abort(HTTPStatus.BAD_REQUEST)

    status_code: HTTPStatus
    try:
        user: User = User.find_by_email(email=user_data.email)
        status_code = HTTPStatus.OK
    except ValueError:
        user: User = User(
            email=user_data.email,
        )
        DBBuilder.session.add(user)
        DBBuilder.session.commit()
        status_code = HTTPStatus.CREATED

    return JWTTokenJSONDictMaker.make(jwt_token=create_access_token(identity=user.email)), status_code


@app.route(Url.REFRESH_TOKEN, endpoint=EndpointName.REFRESH_TOKEN, methods=[HTTPMethod.POST])
@jwt_required()
def refresh_token() -> JWTTokenJSONDictMaker.Dict:
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
    return JWTTokenJSONDictMaker.make(jwt_token=create_access_token(identity=current_user.email))


@app.route(Url.USER_INFO, endpoint=EndpointName.USER_INFO, methods=[HTTPMethod.GET])
@jwt_required()
def user_info() -> UserInfoJSONDictMaker.Dict:
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
        return UserInfoJSONDictMaker.make(user=current_user, exclude_important_info=False)

    try:
        user: User | None = DBBuilder.session.get(User, int(user_id_as_str))
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    if user is None:
        return abort(HTTPStatus.NOT_FOUND)

    return UserInfoJSONDictMaker.make(user=user)


@app.route(Url.USER_CHATS, endpoint=EndpointName.USER_CHATS, methods=[HTTPMethod.GET])
@jwt_required()
def user_chats() -> UserChatsJSONDictMaker.Dict:
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
                unreadCount,
                usersIds: [...],
                lastMessage: {
                    id,
                    chatId,
                    text,
                    creatingDatetime,
                    userId,
                    isRead,
                }
            },
            ...
        ],
    }
    """
    return UserChatsJSONDictMaker.make(
        user_chats=UserChatMatch.user_chats(user_id=current_user.id),
        user_id=current_user.id,
    )


@app.route(Url.CHAT_HISTORY, endpoint=EndpointName.CHAT_HISTORY, methods=[HTTPMethod.GET])
@jwt_required()
def chat_history(chat_id: int) -> ChatHistoryJSONDictMaker.Dict:
    """Сообщения отсортированы по `ChatMessage.creating_datetime` (первое - новейшее).

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
                userId,
                isRead,
            },
            ...
        ],
    }
    """
    offset_from_end: int | None
    try:
        offset_from_end = int(request.args[JSONKey.OFFSET_FROM_END])
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
