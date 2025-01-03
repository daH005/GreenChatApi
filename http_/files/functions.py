from flask import request, abort
from http import HTTPStatus
from werkzeug.utils import secure_filename
from flask_jwt_extended import get_current_user
from pathlib import Path
from typing import Final
from os import listdir
from shutil import rmtree
from functools import wraps

from common.json_keys import JSONKey
from common.hinting import raises
from config import MEDIA_FOLDER
from db.models import User, ChatMessage, UserChatMatch

__all__ = (
    'STORAGE_ID_PATH',
    'save_chat_message_files',
    'chat_message_filenames',
    'chat_message_file_path',
    'check_permissions_decorator',
)

_FILES_PATH: Final[Path] = MEDIA_FOLDER.joinpath('files')
STORAGE_ID_PATH: Final[Path] = _FILES_PATH.joinpath('storage_id')
_MAX_CONTENT_LENGTH: Final[int] = 300 * 1024 * 1024


def save_chat_message_files(storage_id: int | None = None) -> int | None:
    if request.content_length > _MAX_CONTENT_LENGTH:
        return abort(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)

    files = request.files.getlist('files')
    if not files:
        return abort(HTTPStatus.BAD_REQUEST)

    if storage_id is None:
        storage_id: int = _next_storage_id()

    file_folder_path = _FILES_PATH.joinpath(str(storage_id))
    if file_folder_path.exists():
        rmtree(file_folder_path)
    file_folder_path.mkdir()

    secured_filename: str
    for file in files:
        if not file.filename:
            continue

        secured_filename = secure_filename(file.filename)
        file.save(file_folder_path.joinpath(secured_filename))

    return storage_id


def _next_storage_id() -> int:
    if not STORAGE_ID_PATH.exists():
        STORAGE_ID_PATH.write_text('0')

    storage_id: int = int(STORAGE_ID_PATH.read_text())
    STORAGE_ID_PATH.write_text(str(storage_id + 1))

    return storage_id


@raises(FileNotFoundError)
def chat_message_filenames(storage_id: int) -> list[str]:
    return listdir(_FILES_PATH.joinpath(str(storage_id)))


@raises(FileNotFoundError)
def chat_message_file_path(storage_id: int,
                           filename: str,
                           ) -> Path:
    path: Path = _FILES_PATH.joinpath(str(storage_id), filename)
    if not path.exists():
        raise FileNotFoundError
    return path


@raises(PermissionError)
def check_permissions_decorator(func):
    @wraps(func)
    def wrapper():
        try:
            storage_id: int = int(request.args[JSONKey.STORAGE_ID])
        except (KeyError, ValueError):
            return abort(HTTPStatus.BAD_REQUEST)

        user: User = get_current_user()

        try:
            chat_id: int = ChatMessage.by_storage_id(storage_id).chat_id
        except ValueError:
            return abort(HTTPStatus.NOT_FOUND)

        try:
            UserChatMatch.chat_if_user_has_access(
                user_id=user.id,
                chat_id=chat_id,
            )
        except PermissionError:
            return abort(HTTPStatus.FORBIDDEN)

        return func(storage_id)

    return wrapper
