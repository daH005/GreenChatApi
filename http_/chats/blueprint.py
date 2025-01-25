from http import HTTPMethod, HTTPStatus

from flasgger import swag_from
from flask import (
    Blueprint,
    request,
    abort,
)
from flask_jwt_extended import jwt_required

from common.json_keys import JSONKey
from db.builder import db_builder
from db.lists import MessageList
from db.models import (
    User,
    Chat,
    Message,
    UserChatMatch,
    UnreadCount,
)
from db.transaction_retry_decorator import transaction_retry_decorator
from http_.common.apidocs_constants import (
    CHAT_SPECS,
    CHAT_NEW_SPECS,
    CHAT_TYPING_SPECS,
    CHAT_UNREAD_COUNT_SPECS,
    MESSAGE_SPECS,
    MESSAGE_NEW_SPECS,
    MESSAGE_READ_SPECS,
    CHAT_MESSAGES_SPECS,
)
from http_.common.get_current_user import get_current_user
from http_.common.simple_response import make_simple_response
from http_.common.urls import Url
from http_.common.validation import (
    NewChatJSONValidator,
    NewMessageJSONValidator,
)
from http_.common.check_access_decorators import (
    message_access_query_decorator,
    message_access_json_decorator,
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
        except ValueError:
            pass
        else:
            return abort(HTTPStatus.CONFLICT)

    chat: Chat
    chat, *objects = Chat.new_with_all_dependencies(
        data.user_ids,
        name=data.name,
        is_group=data.is_group,
    )
    db_builder.session.add_all([chat, *objects])
    db_builder.session.commit()

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


@chats_bp.route(Url.MESSAGE, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(MESSAGE_SPECS)
@message_access_query_decorator
def message_get(message: Message, _):
    return message.as_json()


@chats_bp.route(Url.MESSAGE_NEW, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(MESSAGE_NEW_SPECS)
@transaction_retry_decorator()
def message_new():
    data: NewMessageJSONValidator = NewMessageJSONValidator.from_json()

    try:
        chat: Chat = Chat.by_id(data.chat_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)

    user: User = get_current_user()
    try:
        chat.check_user_access(user.id)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)

    message: Message = Message.create(
        text=data.text,
        user=user,
        chat=chat,
    )
    db_builder.session.add(message)

    unread_count: UnreadCount
    user_ids = chat.users().ids(exclude_ids=[user.id])
    for user_id in user_ids:
        unread_count = chat.unread_count_of_user(user_id)
        unread_count.increase()

    db_builder.session.commit()

    message.signal_new([user.id, *user_ids])
    chat.signal_new_unread_count(user_ids)

    return message.as_json(), HTTPStatus.CREATED


@chats_bp.route(Url.MESSAGE_READ, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(MESSAGE_READ_SPECS)
@transaction_retry_decorator()
@message_access_json_decorator
def message_read(message: Message,
                 user: User,
                 ):
    sender_read_messages: dict[int, MessageList] = {}
    for history_message in message.chat.unread_messages_until(message.id):
        if history_message.is_read:
            continue

        history_message.read()
        sender_read_messages.setdefault(message.user.id, MessageList()).append(history_message)

    unread_count: UnreadCount = message.chat.unread_count_of_user(user.id)
    new_unread_count: int = message.chat.interlocutor_messages_after_count(message.id, user.id)
    unread_count_is_new: bool = unread_count.value != new_unread_count
    if unread_count_is_new:
        unread_count.set(new_unread_count)

    db_builder.session.commit()

    for user_id, messages in sender_read_messages.items():
        messages.signal_read([user_id])

    if unread_count_is_new:
        message.chat.signal_new_unread_count([user.id])

    return make_simple_response(HTTPStatus.OK)
