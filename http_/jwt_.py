from flask_jwt_extended import JWTManager

from db.builder import db_builder
from db.exceptions import DBEntityNotFound
from db.models import User, AuthToken

__all__ = (
    'jwt',
)

jwt: JWTManager = JWTManager()


@jwt.token_in_blocklist_loader
def token_in_blocklist_callback(_, jwt_payload: dict) -> bool:
    return not AuthToken.exists(jwt_payload['jti'])


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> User | None:
    user_id: int = int(jwt_data['sub'])
    db_builder.session.remove()  # Important: The place chosen by experience way for gunicorn correct work
    try:
        return User.by_id(user_id)
    except DBEntityNotFound:
        return
