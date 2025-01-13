from flask import (
    Blueprint,
    request,
    abort,
)
from http import HTTPMethod, HTTPStatus
from flask_jwt_extended import jwt_required
from flasgger import swag_from

from db.models import UserChatMatch
from common.json_keys import JSONKey
from http_.common.get_current_user import get_current_user
from http_.common.apidocs_constants import CHAT_MESSAGES_SPECS
from http_.common.urls import Url


__all__ = (
    'chats_bp',
)

chats_bp: Blueprint = Blueprint('chats', __name__)


@chats_bp.route(Url.CHAT_MESSAGES, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_SPECS)
def chat_messages():
    try:
        chat_id: int = int(request.args[JSONKey.CHAT_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    offset_from_end: int | None
    try:
        offset_from_end = int(request.args[JSONKey.OFFSET])
        if offset_from_end < 0:
            raise ValueError
    except KeyError:
        offset_from_end = None
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        return UserChatMatch.chat_if_user_has_access(get_current_user().id, chat_id).messages().as_json(offset_from_end)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)
