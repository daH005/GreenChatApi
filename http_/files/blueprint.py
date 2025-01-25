from http import HTTPMethod, HTTPStatus
from pathlib import Path

from flasgger import swag_from
from flask import Blueprint, request, abort, send_file
from flask_jwt_extended import jwt_required

from common.json_keys import JSONKey
from config import MESSAGE_FILES_MAX_CONTENT_LENGTH
from db.models import Message
from http_.common.simple_response import make_simple_response
from http_.common.apidocs_constants import (
    MESSAGE_FILES_UPDATE_SPECS,
    MESSAGE_FILES_NAMES_SPECS,
    MESSAGE_FILES_GET_SPECS,
)
from http_.common.content_length_check_decorator import content_length_check_decorator
from http_.common.urls import Url
from http_.common.check_access_decorators import (
    message_full_access_query_decorator,
    message_access_query_decorator,
)

__all__ = (
    'files_bp',
)

files_bp: Blueprint = Blueprint('files', __name__)


@files_bp.route(Url.MESSAGE_FILES_UPDATE, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(MESSAGE_FILES_UPDATE_SPECS)
@content_length_check_decorator(MESSAGE_FILES_MAX_CONTENT_LENGTH)
@message_full_access_query_decorator
def message_files_update(message: Message, _):
    files = request.files.getlist('files')
    if not files:
        return abort(HTTPStatus.BAD_REQUEST)

    message.storage.save(files)
    message.signal_files(message.chat.users().ids())

    return make_simple_response(HTTPStatus.CREATED)


@files_bp.route(Url.MESSAGE_FILES_NAMES, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(MESSAGE_FILES_NAMES_SPECS)
@message_access_query_decorator
def message_files_names(message: Message, _):
    try:
        return message.storage.filenames()
    except FileNotFoundError:
        return abort(HTTPStatus.NOT_FOUND)


@files_bp.route(Url.MESSAGE_FILES_GET, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(MESSAGE_FILES_GET_SPECS)
@message_access_query_decorator
def message_files_get(message: Message, _):
    try:
        filename: str = request.args[JSONKey.FILENAME]
    except (KeyError, ValueError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        file_path: Path = message.storage.full_path(filename)
    except FileNotFoundError:
        return abort(HTTPStatus.NOT_FOUND)

    return send_file(file_path, download_name=filename, as_attachment=True)
