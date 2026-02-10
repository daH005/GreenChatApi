from http import HTTPMethod, HTTPStatus

from flasgger import swag_from
from flask import (
    Blueprint,
    abort,
    request,
)
from flask_jwt_extended import jwt_required

from common.json_keys import JSONKey
from db.builders import db_sync_builder
from db.exceptions import DBEntityNotFoundException
from db.models import (
    User,
    Chat,
    UserChatMatch,
)
from db.transaction_retry_decorator import transaction_retry_decorator
from http_.common.apidocs_constants import (
    CHAT_SPECS,
    CHAT_BY_INTERLOCUTOR_SPECS,
    CHAT_NEW_SPECS,
    CHAT_TYPING_SPECS,
    CHAT_UNREAD_COUNT_SPECS,
    CHAT_MESSAGES_SPECS,
)
from http_.common.get_current_user import get_current_user
from http_.common.simple_response import make_simple_response
from http_.common.urls import Url
from http_.common.validation import NewChatJSONValidator, OffsetSizeJSONValidator
from http_.common.check_access_decorators import (
    chat_access_query_decorator,
    chat_access_json_decorator,
)

__all__ = (
    'chats_bp',
)

chats_bp: Blueprint = Blueprint('chats', __name__)


@chats_bp.route(Url.CHAT, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_SPECS)
@chat_access_query_decorator
def chat_get(chat: Chat,
             user: User,
             ):
    return chat.as_json(user.id)


@chats_bp.route(Url.CHAT_BY_INTERLOCUTOR, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_BY_INTERLOCUTOR_SPECS)
def chat_by_interlocutor():
    try:
        interlocutor_id: int = int(request.args[JSONKey.INTERLOCUTOR_ID])
    except (KeyError, ValueError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        User.by_id(interlocutor_id)
    except DBEntityNotFoundException:
        return abort(HTTPStatus.NOT_FOUND)

    current_user: User = get_current_user()
    try:
        return Chat.between_users(current_user.id, interlocutor_id).as_json(current_user.id)
    except DBEntityNotFoundException:
        return abort(HTTPStatus.NOT_FOUND)


@chats_bp.route(Url.CHAT_NEW, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(CHAT_NEW_SPECS)
@transaction_retry_decorator()
def chat_new():
    data: NewChatJSONValidator = NewChatJSONValidator.from_json()

    user: User = get_current_user()
    if user.id not in data.user_ids:
        data.user_ids.insert(0, user.id)

    if not data.is_group:
        if len(data.user_ids) != 2:
            return abort(HTTPStatus.BAD_REQUEST)

        try:
            UserChatMatch.private_chat_between_users(*data.user_ids)
        except DBEntityNotFoundException:
            pass
        else:
            return abort(HTTPStatus.CONFLICT)

    chat, objects = Chat.new_with_all_dependencies(
        data.user_ids,
        name=data.name,
        is_group=data.is_group,
    )
    db_sync_builder.session.add_all([chat, *objects])
    db_sync_builder.session.commit()

    chat.signal_new(data.user_ids)
    return chat.as_json(user.id), HTTPStatus.CREATED


@chats_bp.route(Url.CHAT_TYPING, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(CHAT_TYPING_SPECS)
@chat_access_json_decorator
def typing(chat: Chat,
           user: User,
           ):
    user_ids: list[int] = chat.users().ids(exclude_ids=[user.id])
    chat.signal_typing(user_ids, user_id=user.id)

    return make_simple_response(HTTPStatus.OK)


@chats_bp.route(Url.CHAT_UNREAD_COUNT, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_UNREAD_COUNT_SPECS)
@chat_access_query_decorator
def unread_count_get(chat: Chat,
                     user: User,
                     ):
    try:
        return {
            JSONKey.UNREAD_COUNT: chat.unread_count_of_user(user.id),
        }
    except DBEntityNotFoundException:
        return abort(HTTPStatus.NOT_FOUND)


@chats_bp.route(Url.CHAT_MESSAGES, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_SPECS)
@chat_access_query_decorator
def messages_get(chat: Chat, _):
    data: OffsetSizeJSONValidator = OffsetSizeJSONValidator.from_args()
    return chat.messages(data.offset, data.size).as_json()
