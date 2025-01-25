from http import HTTPMethod
from pathlib import Path
from typing import Final

from flasgger import swag_from
from flask import Blueprint
from flask_jwt_extended import jwt_required

from config import (
    STATIC_FOLDER,
    MEDIA_FOLDER,
    USER_BACKGROUND_MAX_CONTENT_LENGTH,
)
from http_.common.apidocs_constants import (
    USER_BACKGROUND_SPECS,
    USER_BACKGROUND_EDIT_SPECS,
)
from http_.common.content_length_check_decorator import content_length_check_decorator
from http_.common.get_current_user import get_current_user
from http_.common.urls import Url
from http_.common.user_images_abstract_endpoints import get_user_image, edit_user_image

__all__ = (
    'backgrounds_bp',
)

backgrounds_bp: Blueprint = Blueprint('backgrounds', __name__)

_DEFAULT_BACKGROUND_PATH: Final[Path] = STATIC_FOLDER.joinpath('default_background.jpg')
_BACKGROUNDS_PATH: Final[Path] = MEDIA_FOLDER.joinpath('backgrounds')


@backgrounds_bp.route(Url.USER_BACKGROUND, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_BACKGROUND_SPECS)
def user_background():
    return get_user_image(
        get_current_user().id,
        _DEFAULT_BACKGROUND_PATH,
        _BACKGROUNDS_PATH,
    )


@backgrounds_bp.route(Url.USER_BACKGROUND_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_BACKGROUND_EDIT_SPECS)
@content_length_check_decorator(USER_BACKGROUND_MAX_CONTENT_LENGTH)
def user_background_edit():
    return edit_user_image(_BACKGROUNDS_PATH)
