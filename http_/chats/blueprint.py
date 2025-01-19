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
    MessageStorage,
    UserChatMatch,
    UnreadCount,
)
from db.transaction_retry_decorator import transaction_retry_decorator
from http_.common.apidocs_constants import (
    CHAT_SPECS,
    CHAT_NEW_SPECS,
    CHAT_TYPING_SPECS,
    CHAT_UNREAD_COUNT_SPECS,
    CHAT_MESSAGE_SPECS,
    CHAT_MESSAGE_NEW_SPECS,
    CHAT_MESSAGE_READ_SPECS,
    CHAT_MESSAGES_SPECS,
)
from http_.common.get_current_user import get_current_user
from http_.common.simple_response import make_simple_response
from http_.common.urls import Url
from http_.common.validation import (
    NewChatJSONValidator,
    NewMessageJSONValidator,
)

__all__ = (
    'chats_bp',
)

chats_bp: Blueprint = Blueprint('chats', __name__)


@chats_bp.route(Url.CHAT, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_SPECS)
def chat_get():
    try:
        chat_id: int = int(request.args[JSONKey.CHAT_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        chat: Chat = Chat.by_id(chat_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)

    user: User = get_current_user()
    try:
        chat.check_user_access(user.id)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)

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

    return make_simple_response(HTTPStatus.CREATED)


@chats_bp.route(Url.CHAT_TYPING, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(CHAT_TYPING_SPECS)
def typing():
    try:
        chat_id: int = int(request.json[JSONKey.CHAT_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        chat: Chat = Chat.by_id(chat_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)

    user: User = get_current_user()
    try:
        chat.check_user_access(user.id)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)

    user_ids: list[int] = chat.users().ids(exclude_ids=[user.id])
    chat.signal_typing(user_ids, user_id=user.id)

    return make_simple_response(HTTPStatus.OK)


@chats_bp.route(Url.CHAT_UNREAD_COUNT, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_UNREAD_COUNT_SPECS)
def unread_count_get():
    try:
        chat_id: int = int(request.args[JSONKey.CHAT_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        chat: Chat = Chat.by_id(chat_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)

    user: User = get_current_user()
    try:
        chat.check_user_access(user.id)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)

    unread_count: UnreadCount = chat.unread_count_of_user(user.id)
    return unread_count.as_json()


@chats_bp.route(Url.CHAT_MESSAGE, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGE_SPECS)
def message_get():
    try:
        message_id: int = int(request.args[JSONKey.MESSAGE_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        message: Message = Message.by_id(message_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)

    try:
        message.chat.check_user_access(get_current_user().id)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)

    return message.as_json()


@chats_bp.route(Url.CHAT_MESSAGE_NEW, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(CHAT_MESSAGE_NEW_SPECS)
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

    storage: MessageStorage | None
    if data.storage_id:
        try:
            storage = MessageStorage.by_id(data.storage_id)
        except ValueError:
            return abort(HTTPStatus.NOT_FOUND)
        if storage.message:
            return abort(HTTPStatus.CONFLICT)
    else:
        storage = None

    message: Message = Message.create(
        text=data.text,
        user=user,
        chat=chat,
        storage=storage,
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

    return make_simple_response(HTTPStatus.CREATED)


@chats_bp.route(Url.CHAT_MESSAGE_READ, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(CHAT_MESSAGE_READ_SPECS)
@transaction_retry_decorator()
def message_read():
    try:
        message_id: int = int(request.json[JSONKey.MESSAGE_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        message: Message = Message.by_id(message_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)

    user: User = get_current_user()
    try:
        message.chat.check_user_access(user.id)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)

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


@chats_bp.route(Url.CHAT_MESSAGES, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(CHAT_MESSAGES_SPECS)
def messages_get():
    try:
        chat_id: int = int(request.args[JSONKey.CHAT_ID])
    except (ValueError, KeyError):
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        chat: Chat = Chat.by_id(chat_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)

    offset: int | None
    try:
        offset = int(request.args[JSONKey.OFFSET])
        if offset < 0:
            raise ValueError
    except KeyError:
        offset = None
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST)

    try:
        chat.check_user_access(get_current_user().id)
    except PermissionError:
        return abort(HTTPStatus.FORBIDDEN)

    return chat.messages(offset=offset).as_json()
