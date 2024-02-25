from pydantic import ValidationError

from api.config import HOST, WEBSOCKET_PORT
from api.hinting import raises
from api.json_ import (
    ChatInfoJSONDictMaker,
    ChatMessageJSONDictMaker,
    ChatMessageTypingJSONDictMaker,
)
from api.db.models import (
    session,
    User,
    Chat,
    UserChatMatch,
)
from api.db.alembic_.init import make_migrations
from api.websocket_.base import WebSocketServer
from api.websocket_.messages import MessageType
from api.websocket_.funcs import (
    users_ids_of_chat_by_id,
    make_chat_message_and_add_to_session,
    interlocutors_ids_for_user_by_id,
)
from api.websocket_.validation import (
    UserIdInfo,
    NewChat,
    NewChatMessage,
    ChatIdInfo,
)

server = WebSocketServer(
    host=HOST,
    port=WEBSOCKET_PORT,
)

users_ids_and_potential_interlocutors_ids = {}


@server.first_connection_handler
async def first_connection_handler(user: User) -> None:
    interlocutors_ids: list[int] = interlocutors_ids_for_user_by_id(user_id=user.id)

    await server.send_to_many_users(
        users_ids=interlocutors_ids + users_ids_and_potential_interlocutors_ids.get(user.id, []),
        message=MessageType.INTERLOCUTORS_ONLINE_STATUSES.make_json_dict({
            user.id: True,
        })
    )

    result_data = {}
    for interlocutor_id in interlocutors_ids:
        if server.user_have_connections(interlocutor_id):
            result_data[interlocutor_id] = True

    await server.send_to_one_user(
        user_id=user.id,
        message=MessageType.INTERLOCUTORS_ONLINE_STATUSES.make_json_dict(result_data)
    )


@server.full_disconnection_handler
async def full_disconnection_handler(user: User) -> None:
    interlocutors_ids: list[int] = interlocutors_ids_for_user_by_id(user_id=user.id)

    await server.send_to_many_users(
        users_ids=interlocutors_ids + users_ids_and_potential_interlocutors_ids.get(user.id, []),
        message=MessageType.INTERLOCUTORS_ONLINE_STATUSES.make_json_dict({
            user.id: False,
        })
    )


@server.common_handler(MessageType.ONLINE_STATUS_TRACING_ADDING)
@raises(ValidationError)
async def online_status_tracing_adding(user: User, data: dict) -> None:
    data: UserIdInfo = UserIdInfo(**data)
    users_ids_and_potential_interlocutors_ids.setdefault(data.user_id, []).append(user.id)

    await server.send_to_one_user(
        user_id=user.id,
        message=MessageType.INTERLOCUTORS_ONLINE_STATUSES.make_json_dict({
            data.user_id: server.user_have_connections(user_id=data.user_id)
        })
    )


@server.common_handler(MessageType.NEW_CHAT)
@raises(ValidationError, ValueError)
async def new_chat(user: User, data: dict) -> None:
    data: NewChat = NewChat(**data)

    if user.id not in data.users_ids:
        raise ValueError

    if not data.is_group and len(data.users_ids) > 2:
        raise ValueError

    try:
        if len(data.users_ids) == 2:
            UserChatMatch.find_private_chat(*data.users_ids)
    except ValueError:
        pass  # Чата нет, значит всё идёт по плану - создаём.
    else:
        raise ValueError

    chat: Chat = Chat(
        name=data.name,
        is_group=data.is_group,
    )
    session.add(chat)
    session.flush()

    matches = []
    for id_ in data.users_ids:
        match = UserChatMatch(
            user_id=id_,
            chat_id=chat.id,
        )
        matches.append(match)

    session.add_all(matches)

    make_chat_message_and_add_to_session(
        text=data.text,
        user_id=user.id,
        chat_id=chat.id,
    )

    session.commit()

    result_data = ChatInfoJSONDictMaker.make(chat=chat)
    await server.send_to_many_users(
        users_ids=data.users_ids,
        message=MessageType.NEW_CHAT.make_json_dict(result_data)
    )

    for user_id in data.users_ids:
        cur_users_ids = [*data.users_ids]
        cur_users_ids.remove(user_id)

        await server.send_to_one_user(
            user_id=user_id,
            message=MessageType.INTERLOCUTORS_ONLINE_STATUSES.make_json_dict({
                id_: server.user_have_connections(user_id=id_) for id_ in cur_users_ids
            })
        )


@server.common_handler(MessageType.NEW_CHAT_MESSAGE)
@raises(ValidationError, PermissionError, ValueError)
async def new_chat_message(user: User, data: dict) -> None:
    data: NewChatMessage = NewChatMessage(**data)

    chat: Chat = UserChatMatch.chat_if_user_has_access(
        user_id=user.id,
        chat_id=data.chat_id,
    )

    chat_message = make_chat_message_and_add_to_session(
        text=data.text,
        user_id=user.id,
        chat_id=chat.id,
    )
    session.commit()

    result_data = ChatMessageJSONDictMaker.make(chat_message=chat_message)
    await server.send_to_many_users(
        users_ids=users_ids_of_chat_by_id(chat_id=chat.id),
        message=MessageType.NEW_CHAT_MESSAGE.make_json_dict(result_data)
    )


@server.common_handler(MessageType.NEW_CHAT_MESSAGE_TYPING)
@raises(ValidationError, PermissionError, ValueError)
async def new_chat_message_typing(user: User, data: dict) -> None:
    data: ChatIdInfo = ChatIdInfo(**data)

    chat: Chat = UserChatMatch.chat_if_user_has_access(
        user_id=user.id,
        chat_id=data.chat_id,
    )

    ids = users_ids_of_chat_by_id(chat_id=chat.id)
    ids.remove(user.id)

    result_data = ChatMessageTypingJSONDictMaker.make(chat_id=chat.id, user=user)
    await server.send_to_many_users(
        users_ids=ids,
        message=MessageType.NEW_CHAT_MESSAGE_TYPING.make_json_dict(result_data)
    )


if __name__ == '__main__':
    make_migrations()
    server.run()
