from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from config import (
    CORS_ORIGINS,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES,
    JWT_REFRESH_TOKEN_EXPIRES,
)
from http_.urls import Url
from http_.jwt_ import jwt
from http_.email.blueprint import (
    bp as email_bp,
)
from http_.avatars.blueprint import (
    bp as avatars_bp,
)
from http_.backgrounds.blueprint import (
    bp as backgrounds_bp,
)
from http_.general.blueprint import (
    bp as general_bp,
)
from http_.files.blueprint import (
    bp as files_bp,
)

__all__ = (
    'create_app',
)


def create_app(name: str) -> Flask:
    app: Flask = Flask(name)
    _init_app_config_and_options(app)
    _init_blueprints(app)
    _init_jwt(app)
    _init_cors(app)
    _init_swagger(app)
    return app


def _init_app_config_and_options(app: Flask) -> None:
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


def _init_jwt(app: Flask) -> None:
    jwt.init_app(app)


def _init_cors(app: Flask) -> None:
    CORS(app, origins=CORS_ORIGINS, supports_credentials=True, expose_headers=['Set-Cookie'])


def _init_swagger(app: Flask) -> None:
    Swagger(app)


def _init_blueprints(app: Flask) -> None:
    for bp in (general_bp, email_bp, avatars_bp, backgrounds_bp, files_bp):
        app.register_blueprint(bp)
