from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
)

from db.i import UserI

__all__ = (
    'UserJWTMixin',
)


class UserJWTMixin(UserI):

    def create_access_token(self) -> str:
        return create_access_token(self._id)

    def create_refresh_token(self) -> str:
        return create_refresh_token(self._id)
