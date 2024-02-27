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
    UnreadCount,
)
from api.db.alembic_.init import make_migrations
from api.websocket_.base import WebSocketServer
from api.websocket_.messages import MessageType
from api.websocket_.funcs import (
    users_ids_of_chat_by_id,
    make_chat_message_and_add_to_session,
    interlocutors_ids_for_user_by_id,
    make_online_statuses_data,
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

    result_data = make_online_statuses_data(
        server=server,
        users_ids=interlocutors_ids,
    )
    if not result_data:
        return

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

    if len(data.users_ids) == 2:
        try:
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

    for user_id in data.users_ids:
        match: UserChatMatch = UserChatMatch(
            user_id=user_id,
            chat_id=chat.id,
        )
        session.add(match)
        session.flush()

        value = 1
        if user_id == user.id:
            value = 0

        unread_count: UnreadCount = UnreadCount(
            user_chat_match_id=match.id,
            value=value,
        )
        session.add(unread_count)

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

    result_data = make_online_statuses_data(
        server=server,
        users_ids=data.users_ids,
    )
    for user_id in data.users_ids:
        if user_id not in result_data:  # we are not online
            continue

        cur_result_data = {**result_data}
        cur_result_data.pop(user_id)

        if not cur_result_data:  # all interlocutors are not online
            continue

        await server.send_to_one_user(
            user_id=user_id,
            message=MessageType.INTERLOCUTORS_ONLINE_STATUSES.make_json_dict(cur_result_data)
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

    for cur_user in chat.users():
        if cur_user.id == user.id:
            continue
        chat.unread_count_for_user(user_id=cur_user.id).value += 1

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

    users_ids = users_ids_of_chat_by_id(chat_id=chat.id)
    users_ids.remove(user.id)

    result_data = ChatMessageTypingJSONDictMaker.make(chat_id=chat.id, user_id=user.id)
    await server.send_to_many_users(
        users_ids=users_ids,
        message=MessageType.NEW_CHAT_MESSAGE_TYPING.make_json_dict(result_data)
    )


if __name__ == '__main__':
    make_migrations()
    server.run()
