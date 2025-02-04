from copy import deepcopy

__all__ = (
    'recursive_fill_func_values_of_dict',
)


def recursive_fill_func_values_of_dict(dct: dict) -> dict:
    dct = deepcopy(dct)
    for key, value in dct.items():
        if callable(value):
            dct[key] = value()
        elif isinstance(value, dict):
            dct[key] = recursive_fill_func_values_of_dict(value)
    return dct
