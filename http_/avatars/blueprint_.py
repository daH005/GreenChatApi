from flask import (
    Blueprint,
    send_file,
    request,
    abort,
    Response,
)
from werkzeug.utils import secure_filename
from http import HTTPMethod, HTTPStatus
from flask_jwt_extended import jwt_required, current_user
from flasgger import swag_from
from typing import Final
from pathlib import Path

from api.common.json_ import JSONKey
from api.db.models import User
from api.config import STATIC_FOLDER, MEDIA_FOLDER
from api.http_.endpoints import Url, EndpointName

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
@swag_from()
def user_avatar() -> Response | None:
    try:
        user_id: str = request.args[JSONKey.USER_ID]
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    avatar_filename: str = user_id + AVATARS_EXTENSION
    avatar_path: Path = AVATARS_PATH.joinpath(avatar_filename)
    if avatar_path.exists():
        return send_file(avatar_path)

    return send_file(DEFAULT_AVATAR_PATH)
