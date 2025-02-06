__all__ = (
    'DBEntityNotFound',
    'DBEntityIsForbidden',
)


class DBEntityNotFound(Exception):
    pass


class DBEntityIsForbidden(Exception):
    pass
