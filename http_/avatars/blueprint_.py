from flask import (
    Blueprint,
    send_file,
    request,
    abort,
    Response,
)
from http import HTTPMethod, HTTPStatus
from flask_jwt_extended import jwt_required, current_user
from flasgger import swag_from
from typing import Final
from pathlib import Path

from api.config import STATIC_FOLDER, MEDIA_FOLDER
from api.common.json_ import JSONKey, SimpleResponseStatusJSONDictMaker
from api.db.models import User
from api.http_.endpoints import Url, EndpointName
from api.http_.apidocs_constants import (
    USER_AVATAR_SPECS,
    USER_EDIT_AVATAR_SPECS,
)

__all__ = (
    'bp',
)

current_user: User

bp: Blueprint = Blueprint('avatars', __name__)

AVATARS_EXTENSION: Final[str] = '.jpg'
DEFAULT_AVATAR_PATH: Final[Path] = STATIC_FOLDER.joinpath('default_avatar.jpg')
AVATARS_PATH: Final[Path] = MEDIA_FOLDER.joinpath('avatars')


@bp.route(Url.USER_AVATAR, endpoint=EndpointName.USER_AVATAR, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_AVATAR_SPECS)
def user_avatar() -> Response | None:
    try:
        user_id_as_str: str = request.args[JSONKey.USER_ID]
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    avatar_path: Path = _make_avatar_path(user_id_as_str=user_id_as_str)
    if avatar_path.exists():
        return send_file(avatar_path)

    return send_file(DEFAULT_AVATAR_PATH)


@bp.route(Url.USER_EDIT_AVATAR, endpoint=EndpointName.USER_EDIT_AVATAR, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_EDIT_AVATAR_SPECS)
def user_edit_avatar() -> SimpleResponseStatusJSONDictMaker.Dict:
    avatar_path: Path = _make_avatar_path(user_id_as_str=str(current_user.id))
    with open(avatar_path, 'wb') as f:
        f.write(request.data)

    return SimpleResponseStatusJSONDictMaker.make(status=HTTPStatus.OK)


def _make_avatar_path(user_id_as_str: str) -> Path:
    avatar_filename: str = user_id_as_str + AVATARS_EXTENSION
    avatar_path: Path = AVATARS_PATH.joinpath(avatar_filename)
    return avatar_path
