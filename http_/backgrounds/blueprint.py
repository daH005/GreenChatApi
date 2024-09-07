from flask import (
    Blueprint,
    Response,
)
from http import HTTPMethod
from flask_jwt_extended import jwt_required, current_user
from flasgger import swag_from
from typing import Final
from pathlib import Path

from api.config import STATIC_FOLDER, MEDIA_FOLDER
from api.common.json_ import SimpleResponseStatusJSONDictMaker
from api.db.models import User
from api.http_.urls import Url
from api.http_.apidocs_constants import (
    USER_BACKGROUND_SPECS,
    USER_BACKGROUND_EDIT_SPECS,
)
from api.http_.user_images_common import get_user_image, edit_user_image

__all__ = (
    'bp',
)

current_user: User

bp: Blueprint = Blueprint('backgrounds', __name__)

_DEFAULT_BACKGROUND_PATH: Final[Path] = STATIC_FOLDER.joinpath('default_background.jpg')
_BACKGROUNDS_PATH: Final[Path] = MEDIA_FOLDER.joinpath('backgrounds')


@bp.route(Url.USER_BACKGROUND, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(USER_BACKGROUND_SPECS)
def user_background() -> Response | None:
    return get_user_image(
        user_id_as_str=str(current_user.id),
        default_path=_DEFAULT_BACKGROUND_PATH,
        folder_path=_BACKGROUNDS_PATH,
    )


@bp.route(Url.USER_BACKGROUND_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(USER_BACKGROUND_EDIT_SPECS)
def user_background_edit() -> SimpleResponseStatusJSONDictMaker.Dict:
    return edit_user_image(folder_path=_BACKGROUNDS_PATH)
