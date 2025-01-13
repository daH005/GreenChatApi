from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from typing import Final

from PIL import Image, UnidentifiedImageError
from flask import (
    send_file,
    request,
    abort,
    Response,
)

from db.models import User
from http_.common.get_current_user import get_current_user
from http_.common.simple_response import make_simple_response

__all__ = (
    'get_user_image',
    'edit_user_image',
)

_EXTENSION: Final[str] = '.jpg'


def get_user_image(user_id: int,
                   default_path: Path,
                   folder_path: Path,
                   ) -> Response:
    try:
        User.by_id(user_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)

    path: Path = _make_user_image_path(str(user_id), folder_path)
    if path.exists():
        return send_file(path)

    return send_file(default_path)


def edit_user_image(folder_path: Path) -> Response:
    if not request.data:
        return abort(HTTPStatus.BAD_REQUEST)

    if not request.headers.get('Content-Type', '').startswith('image/'):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        Image.open(BytesIO(request.data)).verify()
    except UnidentifiedImageError:
        return abort(HTTPStatus.BAD_REQUEST)

    avatar_path: Path = _make_user_image_path(str(get_current_user().id), folder_path)
    avatar_path.write_bytes(request.data)

    return make_simple_response(HTTPStatus.OK)


def _make_user_image_path(user_id_as_str: str,
                          folder_path: Path,
                          ) -> Path:
    filename: str = user_id_as_str + _EXTENSION
    path: Path = folder_path.joinpath(filename)
    return path
