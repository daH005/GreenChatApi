from flask import Blueprint, request, abort, send_file
from http import HTTPMethod, HTTPStatus
from flasgger import swag_from
from flask_jwt_extended import jwt_required
from pathlib import Path

from config import CHAT_MESSAGE_FILES_MAX_CONTENT_LENGTH
from common.json_keys import JSONKey
from db.transaction_retry_decorator import transaction_retry_decorator
from db.models import ChatMessageStorage
from db.builder import db_builder
from http_.common.urls import Url
from http_.common.apidocs_constants import (
    CHAT_MESSAGES_FILES_SAVE_SPECS,
    CHAT_MESSAGES_FILES_NAMES_SPECS,
    CHAT_MESSAGES_FILES_GET_SPECS,
)
from http_.common.content_length_check_decorator import content_length_check_decorator
from http_.files.check_permissions_decorator import check_permissions_decorator

__all__ = (
    'files_bp',
)

files_bp: Blueprint = Blueprint('files', __name__)


@files_bp.route(Url.CHAT_MESSAGES_FILES_SAVE, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_SAVE_SPECS)
@content_length_check_decorator(CHAT_MESSAGE_FILES_MAX_CONTENT_LENGTH)
@transaction_retry_decorator()
def chat_messages_files_save():
    files = request.files.getlist('files')
    if not files:
        return abort(HTTPStatus.BAD_REQUEST)

    storage: ChatMessageStorage = ChatMessageStorage()
    db_builder.session.add(storage)
    db_builder.session.commit()

    storage.save(files)
    return {
        JSONKey.STORAGE_ID: storage.id,
    }, HTTPStatus.CREATED


@files_bp.route(Url.CHAT_MESSAGES_FILES_NAMES, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_NAMES_SPECS)
@check_permissions_decorator
def chat_messages_files_names(storage: ChatMessageStorage):
    try:
        return {
            JSONKey.FILENAMES: storage.filenames(),
        }
    except FileNotFoundError:
        return abort(HTTPStatus.NOT_FOUND)


@files_bp.route(Url.CHAT_MESSAGES_FILES_GET, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_GET_SPECS)
@check_permissions_decorator
def chat_messages_files_get(storage: ChatMessageStorage):
    try:
        filename: str = request.args[JSONKey.FILENAME]
    except (KeyError, ValueError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        file_path: Path = storage.full_path(filename)
    except FileNotFoundError:
        return abort(HTTPStatus.NOT_FOUND)

    return send_file(file_path, download_name=filename, as_attachment=True)
