from flask import (
    Blueprint,
    send_file,
    request,
    Response,
)
from http import HTTPMethod, HTTPStatus
from flask_jwt_extended import jwt_required, current_user
from flasgger import swag_from
from typing import Final
from pathlib import Path

from api.config import STATIC_FOLDER, MEDIA_FOLDER
from api.common.json_ import SimpleResponseStatusJSONDictMaker
from api.db.models import User
from api.http_.endpoints import Url, EndpointName
from api.http_.apidocs_constants import (
    USER_BACKGROUND_SPECS,
    USER_EDIT_BACKGROUND_SPECS,
)

__all__ = (
    'bp',
)

current_user: User

bp: Blueprint = Blueprint('backgrounds', __name__)

BACKGROUNDS_EXTENSION: Final[str] = '.jpg'
DEFAULT_BACKGROUND_PATH: Final[Path] = STATIC_FOLDER.joinpath('default_background.jpg')
BACKGROUNDS_PATH: Final[Path] = MEDIA_FOLDER.joinpath('backgrounds')


@bp.route(Url.USER_BACKGROUND, endpoint=EndpointName.USER_BACKGROUND, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_BACKGROUND_SPECS)
def user_background() -> Response | None:
    user_id_as_str: str = str(current_user.id)

    avatar_path: Path = _make_background_path(user_id_as_str=user_id_as_str)
    if avatar_path.exists():
        return send_file(avatar_path)

    return send_file(DEFAULT_BACKGROUND_PATH)


@bp.route(Url.USER_EDIT_BACKGROUND, endpoint=EndpointName.USER_EDIT_BACKGROUND, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_EDIT_BACKGROUND_SPECS)
def user_edit_background() -> SimpleResponseStatusJSONDictMaker.Dict:
    avatar_path: Path = _make_background_path(user_id_as_str=str(current_user.id))
    with open(avatar_path, 'wb') as f:
        f.write(request.data)

    return SimpleResponseStatusJSONDictMaker.make(status=HTTPStatus.OK)


def _make_background_path(user_id_as_str: str) -> Path:
    background_filename: str = user_id_as_str + BACKGROUNDS_EXTENSION
    background_path: Path = BACKGROUNDS_PATH.joinpath(background_filename)
    return background_path
