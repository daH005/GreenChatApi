from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from config import (
    CORS_ORIGINS,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES,
    JWT_REFRESH_TOKEN_EXPIRES,
)
from http_.chats.blueprint import chats_bp
from http_.common.urls import Url
from http_.messages.files.blueprint import files_bp
from http_.jwt_ import jwt
from http_.users.blueprint import users_bp
from http_.messages.blueprint import messages_bp

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
        JWT_REFRESH_COOKIE_PATH=Url.USER_REFRESH_ACCESS,
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
    for bp in (users_bp, chats_bp, messages_bp):
        app.register_blueprint(bp)
