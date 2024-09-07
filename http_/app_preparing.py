from flask_cors import CORS
from flasgger import Swagger

from api.config import (
    CORS_ORIGINS,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES,
    JWT_REFRESH_TOKEN_EXPIRES,
)
from api.http_.urls import Url
from api.http_.jwt_ import jwt
from api.http_.app import app
from api.http_.email.blueprint import (
    bp as email_bp,
)
from api.http_.avatars.blueprint import (
    bp as avatars_bp,
)
from api.http_.backgrounds.blueprint import (
    bp as backgrounds_bp,
)
from api.http_.general.blueprint import (
    bp as general_bp,
)

__all__ = (
    'init_all_dependencies',
)


def init_all_dependencies() -> None:
    _init_app()
    _init_blueprints()
    _init_jwt()
    _init_cors()
    _init_swagger()


def _init_app() -> None:
    app.config.from_mapping(
        JWT_SESSION_COOKIE=False,
        JWT_COOKIE_SECURE=True,
        JWT_COOKIE_CSRF_PROTECT=True,
        JWT_COOKIE_SAMESITE='None',
        JWT_TOKEN_LOCATION=['cookies'],
        JWT_ACCESS_COOKIE_PATH='/',
        JWT_REFRESH_COOKIE_PATH=Url.REFRESH_ACCESS,
        JWT_SECRET_KEY=JWT_SECRET_KEY,
        JWT_ALGORITHM=JWT_ALGORITHM,
        JWT_ACCESS_TOKEN_EXPIRES=JWT_ACCESS_TOKEN_EXPIRES,
        JWT_REFRESH_TOKEN_EXPIRES=JWT_REFRESH_TOKEN_EXPIRES,
    )
    app.app_context().push()
    app.json.ensure_ascii = False


def _init_jwt() -> None:
    jwt.init_app(app)


def _init_cors() -> None:
    CORS(app, origins=CORS_ORIGINS, supports_credentials=True, expose_headers=['Set-Cookie'])


def _init_swagger() -> None:
    Swagger(app)


def _init_blueprints() -> None:
    for bp in (general_bp, email_bp, avatars_bp, backgrounds_bp):
        app.register_blueprint(bp)
