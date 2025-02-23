from http import HTTPMethod, HTTPStatus
from pathlib import Path
from typing import Final

from flasgger import swag_from
from flask import (
    Blueprint,
    request,
    abort,
)
from flask_jwt_extended import jwt_required

from common.json_keys import JSONKey
from config.paths import STATIC_FOLDER, MEDIA_FOLDER
from config.api import USER_AVATAR_MAX_CONTENT_LENGTH
from http_.common.apidocs_constants import (
    USER_AVATAR_SPECS,
    USER_AVATAR_EDIT_SPECS,
)
from http_.common.content_length_check_decorator import content_length_check_decorator
from http_.common.get_current_user import get_current_user
from http_.common.urls import Url
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
    user_id: int
    try:
        user_id = int(request.args[JSONKey.USER_ID])
    except KeyError:
        user_id = get_current_user().id
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    return get_user_image(
        user_id,
        _DEFAULT_AVATAR_PATH,
        _AVATARS_PATH,
    )


@avatars_bp.route(Url.USER_AVATAR_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_AVATAR_EDIT_SPECS)
@content_length_check_decorator(USER_AVATAR_MAX_CONTENT_LENGTH)
def user_avatar_edit():
    return edit_user_image(_AVATARS_PATH)
