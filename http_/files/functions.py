from flask import request
from werkzeug.utils import secure_filename
from pathlib import Path
from typing import Final
from os import listdir, mkdir

from common.hinting import raises
from config import MEDIA_FOLDER

__all__ = (
    'save_chat_message_files',
    'chat_message_filenames',
    'chat_message_file_path',
)

_FILES_PATH: Final[Path] = MEDIA_FOLDER.joinpath('files')
_STORAGE_ID_PATH: Final[Path] = _FILES_PATH.joinpath('storage_id')


def save_chat_message_files() -> int:
    storage_id: int = _next_storage_id()

    secured_filename: str
    file_folder_path: Path
    for file in request.files.getlist('files'):
        if not file.filename:
            continue

        secured_filename = secure_filename(file.filename)

        file_folder_path = _FILES_PATH.joinpath(str(storage_id))
        mkdir(file_folder_path)

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
