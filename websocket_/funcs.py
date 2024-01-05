from re import sub
from typing import Final

__all__ = (
    'clear_text_message',
    'TEXT_MAX_LENGTH',
)

TEXT_MAX_LENGTH: Final[int] = 10_000


def clear_text_message(str_: str) -> str:
    str_ = str_[:TEXT_MAX_LENGTH]
    str_ = sub(r' {2,}', ' ', str_)
    str_ = sub(r'( ?\n ?)+', '\n', str_)
    str_ = str_.strip()
    return str_


if __name__ == "__main__":
    print(clear_text_message(' string__    line-break\n\nnew-line\nnew-line-2\n'))
