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

from config import (
    STATIC_FOLDER,
    MEDIA_FOLDER,
    USER_AVATAR_MAX_CONTENT_LENGTH,
)
from common.json_keys import JSONKey
from http_.common.urls import Url
from http_.common.apidocs_constants import (
    USER_AVATAR_SPECS,
    USER_AVATAR_EDIT_SPECS,
)
from http_.common.content_length_check_decorator import content_length_check_decorator
from http_.common.user_images_abstract_endpoints import get_user_image, edit_user_image

__all__ = (
    'avatars_bp',
)

avatars_bp: Blueprint = Blueprint('avatars', __name__)

_DEFAULT_AVATAR_PATH: Final[Path] = STATIC_FOLDER.joinpath('default_avatar.jpg')
_AVATARS_PATH: Final[Path] = MEDIA_FOLDER.joinpath('avatars')


@avatars_bp.route(Url.USER_AVATAR, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_AVATAR_SPECS)
def user_avatar():
    try:
        user_id_as_str: str = request.args[JSONKey.USER_ID]
    except KeyError:
        return abort(HTTPStatus.BAD_REQUEST)

    return get_user_image(
        user_id_as_str,
        _DEFAULT_AVATAR_PATH,
        _AVATARS_PATH,
    )


@avatars_bp.route(Url.USER_AVATAR_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_AVATAR_EDIT_SPECS)
@content_length_check_decorator(USER_AVATAR_MAX_CONTENT_LENGTH)
def user_avatar_edit():
    return edit_user_image(_AVATARS_PATH)
