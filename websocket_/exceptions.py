__all__ = (
    'InvalidOriginException',
    'JWTNotFoundInCookiesException',
    'UserIdNotFoundInJWTException',
)


class InvalidOriginException(Exception):
    pass


class JWTNotFoundInCookiesException(Exception):
    pass


class UserIdNotFoundInJWTException(Exception):
    pass
