from json import dumps as json_dumps
from pathlib import Path
from uuid import uuid4

from config import BASE_DIR

__all__ = (
    'assert_and_save_jsons_if_failed',
)

_SAVE_FOLDER: Path = BASE_DIR.joinpath('./_tests/_failed_test_jsons')


def assert_and_save_jsons_if_failed(real, expected) -> None:
    try:
        assert real == expected
    except AssertionError:
        _save_jsons(real, expected)
        raise


def _save_jsons(real, expected) -> None:
    uuid: str = str(uuid4())

    _SAVE_FOLDER.joinpath(uuid + '_real.json').write_text(
        json_dumps(real,
                   indent=2,
                   ensure_ascii=False,
                   )
    )

    _SAVE_FOLDER.joinpath(uuid + '_expected.json').write_text(
        json_dumps(expected,
                   indent=2,
                   ensure_ascii=False,
                   )
    )
