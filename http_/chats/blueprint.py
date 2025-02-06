from http import HTTPMethod, HTTPStatus

from flasgger import swag_from
from flask import (
    Blueprint,
    request,
    abort,
)
from flask_jwt_extended import jwt_required

from common.json_keys import JSONKey
from db.builders import db_sync_builder
from db.exceptions import DBEntityNotFoundException
from db.models import (
    User,
    Chat,
    UserChatMatch,
    UnreadCount,
)
from db.transaction_retry_decorator import transaction_retry_decorator
from http_.common.apidocs_constants import (
    CHAT_SPECS,
    CHAT_NEW_SPECS,
    CHAT_TYPING_SPECS,
    CHAT_UNREAD_COUNT_SPECS,
    CHAT_MESSAGES_SPECS,
)
from http_.common.get_current_user import get_current_user
from http_.common.simple_response import make_simple_response
from http_.common.urls import Url
from http_.common.validation import NewChatJSONValidator
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


@chats_bp.route(Url.CHAT_NEW, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(CHAT_NEW_SPECS)
@transaction_retry_decorator()
def chat_new():
    data: NewChatJSONValidator = NewChatJSONValidator.from_json()

    user: User = get_current_user()
    if user.id not in data.user_ids:
        data.user_ids.insert(0, user.id)

    user_ids_len = len(data.user_ids)
    if user_ids_len <= 1:
        return abort(HTTPStatus.BAD_REQUEST)

    if user_ids_len == 2 and not data.is_group:
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
    unread_count: UnreadCount = chat.unread_count_of_user(user.id)
    return unread_count.as_json()


@chats_bp.route(Url.CHAT_MESSAGES, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_SPECS)
@chat_access_query_decorator
def messages_get(chat: Chat, _):
    offset: int | None
    try:
        offset = int(request.args[JSONKey.OFFSET])
        if offset < 0:
            raise ValueError
    except KeyError:
        offset = None
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    return chat.messages(offset=offset).as_json()
