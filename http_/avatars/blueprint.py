from flask import (
    Blueprint,
    request,
    abort,
)
from http import HTTPMethod, HTTPStatus
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from typing import Final
from pathlib import Path

from config import STATIC_FOLDER, MEDIA_FOLDER
from common.json_keys import JSONKey
from http_.urls import Url
from http_.apidocs_constants import (
    USER_AVATAR_SPECS,
    USER_AVATAR_EDIT_SPECS,
)
from http_.user_images_common import get_user_image, edit_user_image

__all__ = (
    'DEFAULT_AVATAR_PATH',
    'bp',
)

bp: Blueprint = Blueprint('avatars', __name__)

DEFAULT_AVATAR_PATH: Final[Path] = STATIC_FOLDER.joinpath('default_avatar.jpg')
_AVATARS_PATH: Final[Path] = MEDIA_FOLDER.joinpath('avatars')


@bp.route(Url.USER_AVATAR, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_AVATAR_SPECS)
def user_avatar():
    try:
        user_id_as_str: str = request.args[JSONKey.USER_ID]
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return get_user_image(
        user_id_as_str=user_id_as_str,
        default_path=DEFAULT_AVATAR_PATH,
        folder_path=_AVATARS_PATH,
    )


@bp.route(Url.USER_AVATAR_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_AVATAR_EDIT_SPECS)
def user_avatar_edit():
    return edit_user_image(folder_path=_AVATARS_PATH)
