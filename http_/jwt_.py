from flask_jwt_extended import JWTManager

from api.db.models import User, BlacklistToken
from api.db.builder import db_builder

__all__ = (
    'jwt',
)

jwt: JWTManager = JWTManager()

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data) -> User | None:
    email: str = jwt_data['sub']
    try:
        return User.by_email(email=email)
    except ValueError:
        return None


@jwt.token_in_blocklist_loader
def token_in_blocklist_callback(_, jwt_payload: dict) -> None:
    jti: str = jwt_payload['jti']
    jti_in_blocklist: str | None = db_builder.session.query(BlacklistToken).filter_by(jti=jti).first()
    return jti_in_blocklist is not None
