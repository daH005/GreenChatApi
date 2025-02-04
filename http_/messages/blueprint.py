from http import HTTPMethod, HTTPStatus

from flasgger import swag_from
from flask import (
    abort,
    Blueprint,
)
from flask_jwt_extended import jwt_required

from db.builder import db_builder
from db.lists import MessageList
from db.models import (
    User,
    Chat,
    Message,
    UnreadCount,
)
from db.transaction_retry_decorator import transaction_retry_decorator
from http_.common.apidocs_constants import (
    MESSAGE_SPECS,
    MESSAGE_NEW_SPECS,
    MESSAGE_EDIT_SPECS,
    MESSAGE_DELETE_SPECS,
    MESSAGE_READ_SPECS,
)
from http_.common.simple_response import make_simple_response
from http_.common.urls import Url
from http_.common.validation import (
    NewMessageJSONValidator,
    EditMessageJSONValidator,
)
from http_.common.check_access_decorators import (
    message_access_query_decorator,
    message_access_json_decorator,
    message_full_access_json_decorator,
    chat_access_json_decorator,
)
from http_.messages.files.blueprint import files_bp

__all__ = (
    'messages_bp',
)

messages_bp: Blueprint = Blueprint('messages', __name__)
messages_bp.register_blueprint(files_bp)


@messages_bp.route(Url.MESSAGE, methods=[HTTPMethod.GET])
@jwt_required()
@swag_from(MESSAGE_SPECS)
@message_access_query_decorator
def message_get(message: Message, _):
    return message.as_json()


@messages_bp.route(Url.MESSAGE_NEW, methods=[HTTPMethod.POST])
@jwt_required()
@swag_from(MESSAGE_NEW_SPECS)
@transaction_retry_decorator()
@chat_access_json_decorator
def message_new(chat: Chat,
                user: User,
                ):
    data: NewMessageJSONValidator = NewMessageJSONValidator.from_json()

    replied_message: Message | None = None
    if data.replied_message_id:
        replied_message = _get_replied_message(data.replied_message_id, chat.id)

    message: Message = Message.create(
        text=data.text,
        user=user,
        chat=chat,
        replied_message=replied_message,
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


@messages_bp.route(Url.MESSAGE_EDIT, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(MESSAGE_EDIT_SPECS)
@transaction_retry_decorator()
@message_full_access_json_decorator
def message_edit(message: Message, _):
    data: EditMessageJSONValidator = EditMessageJSONValidator.from_json()

    if data.text is data.replied_message_id is None:
        return abort(HTTPStatus.BAD_REQUEST)

    if data.text is not None:
        message.set_text(data.text)

    if data.replied_message_id is not None:
        if data.replied_message_id == message.id:
            return abort(HTTPStatus.CONFLICT)
        replied_message: Message = _get_replied_message(data.replied_message_id, message.chat.id)
        message.set_replied_message(replied_message.id)

    db_builder.session.commit()

    message.signal_edit(message.chat.users().ids())
    return make_simple_response(HTTPStatus.OK)


def _get_replied_message(replied_message_id: int,
                         chat_id: int,
                         ) -> Message:
    try:
        replied_message: Message = Message.by_id(replied_message_id)
    except ValueError:
        return abort(HTTPStatus.NOT_FOUND)
    if replied_message.chat.id != chat_id:
        raise abort(HTTPStatus.FORBIDDEN)

    return replied_message


@messages_bp.route(Url.MESSAGE_DELETE, methods=[HTTPMethod.DELETE])
@jwt_required()
@swag_from(MESSAGE_DELETE_SPECS)
@transaction_retry_decorator()
@message_full_access_json_decorator
def message_delete(message: Message, _):
    db_builder.session.delete(message)
    db_builder.session.commit()

    message.signal_delete(message.chat.users().ids())
    return make_simple_response(HTTPStatus.OK)


@messages_bp.route(Url.MESSAGE_READ, methods=[HTTPMethod.PUT])
@jwt_required()
@swag_from(MESSAGE_READ_SPECS)
@transaction_retry_decorator()
@message_access_json_decorator
def message_read(message: Message,
                 user: User,
                 ):
    sender_read_messages: dict[int, MessageList] = {}
    for history_message in message.chat.unread_interlocutor_messages_up_to(message.id, user.id):
        history_message.read()
        sender_read_messages.setdefault(message.user.id, MessageList()).append(history_message)

    unread_count: UnreadCount = message.chat.unread_count_of_user(user.id)

    new_unread_count: int = message.chat.interlocutor_messages_after_count(message.id, user.id)
    unread_count_is_new: bool = new_unread_count < unread_count.value
    if unread_count_is_new:
        unread_count.set(new_unread_count)

    if unread_count_is_new or sender_read_messages:
        db_builder.session.commit()

    for user_id, messages in sender_read_messages.items():
        messages.signal_read([user_id])

    if unread_count_is_new:
        message.chat.signal_new_unread_count([user.id])

    return make_simple_response(HTTPStatus.OK)
