from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
)

__all__ = (
    'UserJWTMixin',
)


class UserJWTMixin:

    def create_access_token(self):
        return create_access_token(self._email)

    def create_refresh_token(self):
        return create_refresh_token(self._email)
