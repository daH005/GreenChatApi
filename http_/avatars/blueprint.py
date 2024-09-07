from flask import (
    Blueprint,
    request,
    abort,
    Response,
)
from http import HTTPMethod, HTTPStatus
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from typing import Final
from pathlib import Path

from api.config import STATIC_FOLDER, MEDIA_FOLDER
from api.common.json_ import JSONKey, SimpleResponseStatusJSONDictMaker
from api.http_.urls import Url
from api.http_.apidocs_constants import (
    USER_AVATAR_SPECS,
    USER_AVATAR_EDIT_SPECS,
)
from api.http_.user_images_common import get_user_image, edit_user_image

__all__ = (
    'bp',
)

bp: Blueprint = Blueprint('avatars', __name__)

_DEFAULT_AVATAR_PATH: Final[Path] = STATIC_FOLDER.joinpath('default_avatar.jpg')
_AVATARS_PATH: Final[Path] = MEDIA_FOLDER.joinpath('avatars')


@bp.route(Url.USER_AVATAR, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_AVATAR_SPECS)
def user_avatar() -> Response | None:
    try:
        user_id_as_str: str = request.args[JSONKey.USER_ID]
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return get_user_image(
        user_id_as_str=user_id_as_str,
        default_path=_DEFAULT_AVATAR_PATH,
        folder_path=_AVATARS_PATH,
    )


@bp.route(Url.USER_AVATAR_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_AVATAR_EDIT_SPECS)
def user_avatar_edit() -> SimpleResponseStatusJSONDictMaker.Dict:
    return edit_user_image(folder_path=_AVATARS_PATH)
