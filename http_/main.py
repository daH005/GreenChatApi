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
current_user: User  # Аннотация прокси-объекта из библиотеки JWT.
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
from api.http_.mail.blueprint_ import bp as mail_bp

# Инициализируем Flask-приложение. Выполняем все необходимые настройки.
app: Flask = Flask(__name__)
app.config.from_mapping(
    JWT_SECRET_KEY=JWT_SECRET_KEY,
    JWT_ALGORITHM=JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES=JWT_ACCESS_TOKEN_EXPIRES,
)
app.json.ensure_ascii = False
# Важно! CORS позволяет обращаться к нашему REST api с других доменов / портов.
CORS(app, origins=CORS_ORIGINS)
# Объект, обеспечивающий OAuth авторизацию.
jwt: JWTManager = JWTManager(app)

# Регистрация подмодулей приложения:
app.register_blueprint(mail_bp)


@jwt.user_identity_loader
def user_identity_lookup(user: User) -> str:
    """Определяет данные, кодирование которых и будет представлять собой JWT-токен."""
    return user.auth_token


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> User | None:
    """Авторизует пользователя, отправившего запрос.
    Библиотека JWT ожидает `None`, поэтому отлавливаем наше собственное исключение.
    """
    identity: str = jwt_data['sub']
    try:
        return User.auth_by_token(auth_token=identity)
    except PermissionError:
        return None


@app.teardown_appcontext
def shutdown_db_session(exception=None) -> None:
    """Закрывает сессию БД после обработки каждого запроса."""
    if exception:
        print(exception)
    session.remove()


@app.errorhandler(HTTPException)
def handle_exception(exception: HTTPException) -> Response:
    """Заменяет все HTML-представления статус-кодов на JSON."""
    response = exception.get_response()
    response.content_type = 'application/json'
    response.data = json_dumps(dict(code=exception.code))
    return response


@app.route(Url.REG, endpoint=EndpointName.REG, methods=[HTTPMethod.POST])
def create_new_user() -> tuple[JWTTokenJSONDict, HTTPStatus.CREATED]:
    """Создаёт нового пользователя по JSON-данным. Возвращает JWT-токен
    для его дальнейшего сохранения у клиента в localStorage и работы с нашим RESTful api + websocket.
    Ожидается JSON с ключами 'username', 'password', 'firstName', 'lastName' и 'email'.
    Отдаёт 409-й статус-код в случаях, если почта / логин уже заняты.
    """
    # Если данные невалидны, то здесь же падает `abort` с 400-м статус-кодом.
    user_data: UserJSONValidator = UserJSONValidator.from_json()
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
    """Проверят занятость логина. Ожидает query-параметр 'username'.
    Возвращает словарь с флагом, обозначающим занятость.
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
    """Проверят занятость почты. Ожидает query-параметр 'email'.
    Возвращает словарь с флагом, обозначающим занятость.
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
    """Авторизует пользователя по логину и паролю. Возвращает JWT-токен
    для его дальнейшего сохранения у клиента в localStorage и работы с нашим RESTful api + websocket.
    Ожидается JSON с ключами 'username' и 'password'.
    """
    # Валидация данных из JSON:
    try:
        username: str = str(request.json[JSONKey.USERNAME])
        password: str = str(request.json[JSONKey.PASSWORD])
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)
    # Проводим авторизацию.
    try:
        auth_user: User = User.auth_by_username_and_password(username, password)
    except ValueError:
        return abort(HTTPStatus.FORBIDDEN)
    # Возвращаем токен для дальнейшего его сохранения у клиента в localStorage.
    return JSONDictPreparer.prepare_jwt_token(jwt_token=create_access_token(identity=auth_user))


@app.route(Url.REFRESH_TOKEN, endpoint=EndpointName.REFRESH_TOKEN, methods=[HTTPMethod.POST])
@jwt_required()
def refresh_token() -> JWTTokenJSONDict:
    """Выдаёт новый JWT-токен для увеличения срока доступности."""
    return JSONDictPreparer.prepare_jwt_token(jwt_token=create_access_token(identity=current_user))


@app.route(Url.USER_INFO, endpoint=EndpointName.USER_INFO, methods=[HTTPMethod.GET])
@jwt_required()
def user_info() -> UserInfoJSONDict:
    """Выдаёт всю доступную информацию о запрашиваемом пользователе.
    Ожидается query-параметр 'id' - ID пользователя. Выдаётся урезанная информация.
    В случае отсутствия параметра 'id' выдаётся расширенная информация об авторизованном пользователе `current_user`.
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
    """Выдаёт все чаты `current_user` (от каждого чата берётся только последнее сообщение).
    Список чатов отсортирован по дате создания последнего сообщения (от позднего к раннему).
    """
    return JSONDictPreparer.prepare_user_chats(
        user_chats=UserChatMatch.user_chats(user_id=current_user.id),
        user_id=current_user.id,
    )


@app.route(Url.CHAT_HISTORY, endpoint=EndpointName.CHAT_HISTORY, methods=[HTTPMethod.GET])
@jwt_required()
def chat_history(chat_id: int) -> ChatHistoryJSONDict:
    """Выдаёт всю историю заданного чата (при условии, что он доступен для `current_user`).
    Ожидается опциональный query-параметр 'offsetFromEnd'.
    """
    # Параметр, определяющий отступ с конца истории.
    offset_from_end: int | None
    try:
        offset_from_end = -int(request.args[JSONKey.OFFSET_FROM_END])
    except KeyError:
        offset_from_end = None
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)
    # Проверка доступа пользователя к заданному чату.
    # Если всё ок, то возвращаем историю.
    try:
        return JSONDictPreparer.prepare_chat_history(
            chat_messages=UserChatMatch.chat_if_user_has_access(user_id=current_user.id,
                                                                chat_id=chat_id).messages[:offset_from_end],
        )
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)


if __name__ == '__main__':
    app.run(HOST, PORT, debug=DEBUG)
