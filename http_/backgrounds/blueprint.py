from line_profiler import profile
from flask import (
    Blueprint,
    Response,
)
from http import HTTPMethod
from flask_jwt_extended import jwt_required, get_current_user
from flasgger import swag_from
from typing import Final
from pathlib import Path

from config import STATIC_FOLDER, MEDIA_FOLDER
from http_.urls import Url
from http_.apidocs_constants import (
    USER_BACKGROUND_SPECS,
    USER_BACKGROUND_EDIT_SPECS,
)
from http_.user_images_common import get_user_image, edit_user_image

__all__ = (
    'DEFAULT_BACKGROUND_PATH',
    'bp',
)

bp: Blueprint = Blueprint('backgrounds', __name__)

DEFAULT_BACKGROUND_PATH: Final[Path] = STATIC_FOLDER.joinpath('default_background.jpg')
_BACKGROUNDS_PATH: Final[Path] = MEDIA_FOLDER.joinpath('backgrounds')


@bp.route(Url.USER_BACKGROUND, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_BACKGROUND_SPECS)
@profile
def user_background() -> Response:
    return get_user_image(
        user_id_as_str=str(get_current_user().id),
        default_path=DEFAULT_BACKGROUND_PATH,
        folder_path=_BACKGROUNDS_PATH,
    )


@bp.route(Url.USER_BACKGROUND_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_BACKGROUND_EDIT_SPECS)
@profile
def user_background_edit() -> Response:
    return edit_user_image(folder_path=_BACKGROUNDS_PATH)
