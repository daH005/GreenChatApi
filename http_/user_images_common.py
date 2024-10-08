from flask import (
    send_file,
    request,
    Response,
)
from http import HTTPStatus
from flask_jwt_extended import get_current_user
from typing import Final
from pathlib import Path

from http_.simple_response import make_simple_response

__all__ = (
    'get_user_image',
    'edit_user_image',
)

_EXTENSION: Final[str] = '.jpg'


def get_user_image(user_id_as_str: str,
                   default_path: Path,
                   folder_path: Path,
                   ) -> Response:
    path: Path = _make_user_image_path(user_id_as_str=user_id_as_str, folder_path=folder_path)
    if path.exists():
        return send_file(path)

    return send_file(default_path)


def edit_user_image(folder_path: Path) -> Response:
    avatar_path: Path = _make_user_image_path(user_id_as_str=str(get_current_user().id), folder_path=folder_path)
    with open(avatar_path, 'wb') as f:
        f.write(request.data)

    return make_simple_response(HTTPStatus.OK)


def _make_user_image_path(user_id_as_str: str,
                          folder_path: Path,
                          ) -> Path:
    filename: str = user_id_as_str + _EXTENSION
    path: Path = folder_path.joinpath(filename)
    return path
