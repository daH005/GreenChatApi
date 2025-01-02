__all__ = (
    'values_of_set_cookie_to_dict',
)


def values_of_set_cookie_to_dict(cookies: list[str]) -> dict[str, str] | None:
    res = {}
    for cookie in cookies:
        key, value = cookie.split(';', maxsplit=1)[0].split('=', maxsplit=1)
        res[key] = value
    return res
