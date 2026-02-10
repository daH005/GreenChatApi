from http import HTTPMethod, HTTPStatus

from flasgger import swag_from
from flask import (
    abort,
    Blueprint,
)
from flask_jwt_extended import jwt_required

from db.builders import db_sync_builder
from db.exceptions import DBEntityNotFoundException
from db.lists import MessageList
from db.models import (
    User,
    Chat,
    Message,
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
    db_sync_builder.session.add(message)
    db_sync_builder.session.commit()

    message.signal_new(
        chat.users().ids(),
    )
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
        message.set_replied_message_id(replied_message.id)

    db_sync_builder.session.commit()

    message.signal_edit(message.chat.users().ids())
    return make_simple_response(HTTPStatus.OK)


def _get_replied_message(replied_message_id: int,
                         chat_id: int,
                         ) -> Message:
    try:
        replied_message: Message = Message.by_id(replied_message_id)
    except DBEntityNotFoundException:
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
    db_sync_builder.session.delete(message)
    db_sync_builder.session.commit()

    message.get_storage().delete_all()
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

    message.chat.set_last_seen_message_id_of_user(user.id, message.id)
    db_sync_builder.session.commit()

    for user_id, messages in sender_read_messages.items():
        messages.signal_read([user_id])
    message.chat.signal_new_unread_count([user.id])

    return make_simple_response(HTTPStatus.OK)
