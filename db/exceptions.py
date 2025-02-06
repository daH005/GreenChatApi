__all__ = (
    'DBEntityNotFoundException',
    'DBEntityIsForbiddenException',
)


class DBEntityNotFoundException(Exception):
    pass


class DBEntityIsForbiddenException(Exception):
    pass
