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


def save_chat_message_files(chat_message_id: int) -> None:
    secured_filename: str
    file_folder_path: Path
    for file in request.files.getlist('files'):
        if not file.filename:
            continue

        secured_filename = secure_filename(file.filename)

        file_folder_path = _FILES_PATH.joinpath(str(chat_message_id))
        mkdir(file_folder_path)

        file.save(file_folder_path.joinpath(secured_filename))


@raises(FileNotFoundError)
def chat_message_filenames(chat_message_id: int) -> list[str]:
    return listdir(_FILES_PATH.joinpath(str(chat_message_id)))


@raises(FileNotFoundError)
def chat_message_file_path(chat_message_id: int,
                           filename: str,
                           ) -> Path:
    path: Path = _FILES_PATH.joinpath(str(chat_message_id), filename)
    if not path.exists():
        raise FileNotFoundError
    return path
