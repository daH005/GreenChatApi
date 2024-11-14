from line_profiler import profile
from flask import Response, Blueprint, request, abort, send_file
from http import HTTPMethod, HTTPStatus
from flasgger import swag_from
from flask_jwt_extended import jwt_required
from pathlib import Path

from common.json_ import (
    JSONKey,
    ChatMessageStorageIdJSONDictMaker,
    ChatMessageFilenamesJSONDictMaker,
)
from http_.urls import Url
from http_.apidocs_constants import (
    CHAT_MESSAGES_FILES_SAVE_SPECS,
    CHAT_MESSAGES_FILES_NAMES_SPECS,
    CHAT_MESSAGES_FILES_GET_SPECS,
)
from http_.files.functions import (
    save_chat_message_files,
    chat_message_filenames,
    chat_message_file_path,
    check_permissions_decorator,
)

__all__ = (
    'bp',
)

bp: Blueprint = Blueprint('files', __name__)


@bp.route(Url.CHAT_MESSAGES_FILES_SAVE, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_SAVE_SPECS)
@profile
def chat_messages_files_save() -> ChatMessageStorageIdJSONDictMaker.Dict:
    storage_id: int = save_chat_message_files()
    return ChatMessageStorageIdJSONDictMaker.make(storage_id)


@bp.route(Url.CHAT_MESSAGES_FILES_NAMES, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_NAMES_SPECS)
@check_permissions_decorator
@profile
def chat_messages_files_names(storage_id: int) -> ChatMessageFilenamesJSONDictMaker.Dict:
    try:
        filenames: list[str] = chat_message_filenames(storage_id)
    except FileNotFoundError:
        return abort(HTTPStatus.NOT_FOUND)

    return ChatMessageFilenamesJSONDictMaker.make(filenames)


@bp.route(Url.CHAT_MESSAGES_FILES_GET, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_GET_SPECS)
@check_permissions_decorator
@profile
def chat_messages_files_get(storage_id: int) -> Response:
    try:
        filename: str = request.args[JSONKey.FILENAME]
    except (KeyError, ValueError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        file_path: Path = chat_message_file_path(storage_id, filename)
    except FileNotFoundError:
        return abort(HTTPStatus.NOT_FOUND)

    return send_file(file_path, as_attachment=True)
