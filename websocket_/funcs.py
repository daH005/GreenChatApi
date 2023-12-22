from re import sub

__all__ = (
    'del_odd_from_str',
)


def del_odd_from_str(str_: str) -> str:
    """Удаляет из строки лишние пробелы и переносы строк. Принцип следующий:
    Строка модифицируется так, чтобы между отдельными словами мог быть либо один пробел, либо один перенос \n.
    Также убираются пробелы и переносы по краям строки.
    """
    str_ = sub(r' {2,}', ' ', str_)
    str_ = sub(r'( ?\n ?)+', '\n', str_)
    str_ = str_.strip()
    return str_


if __name__ == "__main__":
    print(del_odd_from_str(' string__    line-break\n\nnew-line\nnew-line-2\n'))

