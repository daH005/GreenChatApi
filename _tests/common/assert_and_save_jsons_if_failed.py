from json import dumps as json_dumps
from pathlib import Path

from config.paths import BASE_DIR

__all__ = (
    'assert_and_save_jsons_if_failed',
)

_SAVE_FOLDER: Path = BASE_DIR.joinpath('./_tests/_failed_test_jsons')
count: int = 0


def assert_and_save_jsons_if_failed(real, expected) -> None:
    try:
        assert real == expected
    except AssertionError:
        _save_jsons(real, expected)
        raise


def _save_jsons(real, expected) -> None:
    global count

    _SAVE_FOLDER.joinpath(str(count) + '_real.json').write_text(
        json_dumps(real,
                   indent=4,
                   ensure_ascii=False,
                   )
    )

    _SAVE_FOLDER.joinpath(str(count) + '_expected.json').write_text(
        json_dumps(expected,
                   indent=4,
                   ensure_ascii=False,
                   )
    )

    count += 1
