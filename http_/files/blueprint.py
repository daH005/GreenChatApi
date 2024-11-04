from line_profiler import profile
from flask import Response, Blueprint, request, abort, send_file
from http import HTTPMethod, HTTPStatus
from flasgger import swag_from
from flask_jwt_extended import jwt_required

from common.json_ import (
    JSONKey,
    ChatMessageFilenamesJSONDictMaker,
)
from http_.simple_response import make_simple_response
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
)

__all__ = (
    'bp',
)

bp: Blueprint = Blueprint('files', __name__)


@bp.route(Url.CHAT_MESSAGES_FILES_SAVE, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_SAVE_SPECS)
@profile
def chat_messages_files_save() -> Response:
    try:
        chat_message_id: int = int(request.args[JSONKey.CHAT_MESSAGE_ID])
    except (KeyError, ValueError):
        return abort(HTTPStatus.BAD_REQUEST)

    save_chat_message_files(chat_message_id)
    return make_simple_response(HTTPStatus.OK)


@bp.route(Url.CHAT_MESSAGES_FILES_NAMES, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_NAMES_SPECS)
@profile
def chat_messages_files_names() -> ChatMessageFilenamesJSONDictMaker.Dict:
    try:
        chat_message_id: int = int(request.args[JSONKey.CHAT_MESSAGE_ID])
    except (KeyError, ValueError):
        return abort(HTTPStatus.BAD_REQUEST)

    return ChatMessageFilenamesJSONDictMaker.make(chat_message_filenames(chat_message_id))


@bp.route(Url.CHAT_MESSAGES_FILES_GET, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_FILES_GET_SPECS)
@profile
def chat_messages_files_get() -> Response:
    try:
        chat_message_id: int = int(request.args[JSONKey.CHAT_MESSAGE_ID])
        filename: str = request.args[JSONKey.FILENAME]
    except (KeyError, ValueError):
        return abort(HTTPStatus.BAD_REQUEST)

    return send_file(chat_message_file_path(chat_message_id, filename))
