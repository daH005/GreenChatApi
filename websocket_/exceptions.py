__all__ = (
    'InvalidOriginException',
    'JWTNotFoundInCookies',
    'UserIdNotFoundInJWT',
)


class InvalidOriginException(Exception):
    pass


class JWTNotFoundInCookies(Exception):
    pass


class UserIdNotFoundInJWT(Exception):
    pass
