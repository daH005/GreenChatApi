from base64 import b64encode, b64decode
from os import listdir
from shutil import rmtree
from pathlib import Path
from typing import Final

from common.hinting import raises
from config.paths import MEDIA_FOLDER
from db.i import IMessageStorage, IMessageStorageFile

__all__ = (
    'MessageStorage',
)


class MessageStorage(IMessageStorage):
    _FILES_PATH: Final[Path] = MEDIA_FOLDER.joinpath('files')
    _ALTCHARS: bytes = b'-_'

    def __init__(self, message: 'Message') -> None:
        self._message: Message = message

    @property
    def message(self) -> 'Message':
        return self._message

    def exists(self) -> bool:
        return self.path().exists()

    def update(self, files: list['IMessageStorageFile']) -> None:
        folder_path: Path = self.path()
        if not folder_path.exists():
            folder_path.mkdir()

        secured_filename: str
        for file in files:
            if not file.filename:
                continue

            secured_filename = self._encode_filename(file.filename)
            file.save(folder_path.joinpath(secured_filename))

    def delete(self, filenames: list[str]) -> None:
        folder_path: Path = self.path()

        file_path: Path
        for filename in filenames:
            file_path = folder_path.joinpath(self._encode_filename(filename))
            if not file_path.exists():
                continue

            file_path.unlink()

    def delete_all(self) -> None:
        path: Path = self.path()
        if not path.exists():
            return
        rmtree(path)

    @raises(FileNotFoundError)
    def filenames(self) -> list[str]:
        filenames: list[str] = listdir(self.path())
        return [self._decode_filename(filename) for filename in filenames]

    @raises(FileNotFoundError)
    def full_path(self, filename: str) -> Path:
        filename: str = self._encode_filename(filename)
        path: Path = self.path().joinpath(filename)
        if not path.exists():
            raise FileNotFoundError
        return path

    def path(self) -> Path:
        return self._FILES_PATH.joinpath(str(self._message.id))

    def _encode_filename(self, filename: str) -> str:
        return b64encode(filename.encode(), altchars=self._ALTCHARS).decode()

    def _decode_filename(self, filename: str) -> str:
        return b64decode(filename, altchars=self._ALTCHARS).decode()


from db.models import Message  # noqa
