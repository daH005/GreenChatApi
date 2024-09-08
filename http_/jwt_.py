from flask_jwt_extended import JWTManager

from api.db.models import User, BlacklistToken

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
def token_in_blocklist_callback(_, jwt_payload: dict) -> bool:
    return BlacklistToken.exists(jti=jwt_payload['jti'])