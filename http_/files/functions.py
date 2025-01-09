from flask import request, abort
from werkzeug.datastructures.file_storage import FileStorage
from http import HTTPStatus
from werkzeug.utils import secure_filename
from pathlib import Path
from typing import Final
from os import listdir
from shutil import rmtree
from functools import wraps

from common.json_keys import JSONKey
from common.hinting import raises
from config import MEDIA_FOLDER
from db.models import User, ChatMessage
from http_.common.get_current_user import get_current_user

__all__ = (
    'save_files_and_get_storage_id',
    'chat_message_filenames',
    'chat_message_file_path',
    'check_permissions_decorator',
)

_FILES_PATH: Final[Path] = MEDIA_FOLDER.joinpath('files')
_STORAGE_ID_PATH: Final[Path] = _FILES_PATH.joinpath('storage_id')


def save_files_and_get_storage_id(files: list[FileStorage],
                                  storage_id: int | None = None,
                                  ) -> int:
    if storage_id is None:
        storage_id: int = _next_storage_id()

    file_folder_path: Path = _FILES_PATH.joinpath(str(storage_id))
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
    if not _STORAGE_ID_PATH.exists():
        _STORAGE_ID_PATH.write_text('0')

    storage_id: int = int(_STORAGE_ID_PATH.read_text())
    _STORAGE_ID_PATH.write_text(str(storage_id + 1))

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


def check_permissions_decorator(func):
    @wraps(func)
    def wrapper():
        try:
            storage_id: int = int(request.args[JSONKey.STORAGE_ID])
        except (KeyError, ValueError):
            return abort(HTTPStatus.BAD_REQUEST)

        user: User = get_current_user()
        try:
            ChatMessage.by_storage_id(storage_id).chat.check_user_access(user.id)
        except ValueError:
            return abort(HTTPStatus.NOT_FOUND)
        except PermissionError:
            return abort(HTTPStatus.FORBIDDEN)

        return func(storage_id)

    return wrapper
