__all__ = (
    'set_for_test_to_values_and_ids',
)


def set_for_test_to_values_and_ids(set_for_test) -> dict[str, list]:
    attrs = _extract_attrs_without_dunder(set_for_test)

    result: dict[str, list] = {
        'argvalues': [],
        'ids': [],
    }

    argvalues: list
    for attr in attrs:
        argvalues = getattr(set_for_test, attr)
        result['argvalues'] += argvalues
        result['ids'] += [attr] * len(argvalues)

    return result


def _extract_attrs_without_dunder(type_: type) -> tuple[str]:
    attrs = type_.__dict__.keys()
    attrs = filter(lambda x: not x.startswith('_'), attrs)
    return tuple(attrs)
