from flask import Blueprint, request, abort, send_file
from http import HTTPMethod, HTTPStatus
from flasgger import swag_from
from flask_jwt_extended import jwt_required
from pathlib import Path

from config import CHAT_MESSAGE_FILES_MAX_CONTENT_LENGTH
from common.json_keys import JSONKey
from http_.common.urls import Url
from http_.common.apidocs_constants import (
    CHAT_MESSAGES_FILES_SAVE_SPECS,
    CHAT_MESSAGES_FILES_NAMES_SPECS,
    CHAT_MESSAGES_FILES_GET_SPECS,
)
from http_.common.content_length_check_decorator import content_length_check_decorator
from http_.files.functions import (
    save_files_and_get_storage_id,
    chat_message_filenames,
    chat_message_file_path,
    check_permissions_decorator,
)

__all__ = (
    'files_bp',
)

files_bp: Blueprint = Blueprint('files', __name__)


@files_bp.route(Url.CHAT_MESSAGES_FILES_SAVE, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_SAVE_SPECS)
@content_length_check_decorator(CHAT_MESSAGE_FILES_MAX_CONTENT_LENGTH)
def chat_messages_files_save():
    files = request.files.getlist('files')
    if not files:
        return abort(HTTPStatus.BAD_REQUEST)

    storage_id: int = save_files_and_get_storage_id(files)
    return {
        JSONKey.STORAGE_ID: storage_id,
    }, HTTPStatus.CREATED


@files_bp.route(Url.CHAT_MESSAGES_FILES_NAMES, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_NAMES_SPECS)
@check_permissions_decorator
def chat_messages_files_names(storage_id: int):
    try:
        return {
            JSONKey.FILENAMES: chat_message_filenames(storage_id),
        }
    except FileNotFoundError:
        return abort(HTTPStatus.NOT_FOUND)


@files_bp.route(Url.CHAT_MESSAGES_FILES_GET, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_GET_SPECS)
@check_permissions_decorator
def chat_messages_files_get(storage_id: int):
    try:
        filename: str = request.args[JSONKey.FILENAME]
    except (KeyError, ValueError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        file_path: Path = chat_message_file_path(storage_id, filename)
    except FileNotFoundError:
        return abort(HTTPStatus.NOT_FOUND)

    return send_file(file_path, download_name=filename, as_attachment=True)
