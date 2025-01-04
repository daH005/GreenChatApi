from flask_jwt_extended import get_current_user as _get_current_user

from db.models import User

__all__ = (
    'get_current_user',
)


def get_current_user() -> User:
    return _get_current_user()
