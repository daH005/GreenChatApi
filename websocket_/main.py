from pydantic import ValidationError

from api.config import HOST, WEBSOCKET_PORT, DB_URL
from api.hinting import raises
from api.json_ import (
    ChatInfoJSONDictMaker,
    ChatMessageJSONDictMaker,
    ChatMessageTypingJSONDictMaker,
    NewUnreadCountJSONDictMaker,
    ReadChatMessagesJSONDictMaker,
)
from api.db.models import (
    DBBuilder,
    User,
    Chat,
    ChatMessage,
    UserChatMatch,
    UnreadCount,
)
from api.websocket_.base import WebSocketServer
from api.websocket_.messages import MessageType
from api.websocket_.funcs import (
    users_ids_of_chat_by_id,
    make_chat_message_and_add_to_session,
    interlocutors_ids_for_user_by_id,
    make_online_statuses_data,
)
from api.websocket_.validation import (
    UserIdData,
    NewChat,
    NewChatMessage,
    ChatIdData,
    ChatMessageWasReadData,
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
    if result_data:
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
    data: UserIdData = UserIdData(**data)
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
    DBBuilder.session.add(chat)
    DBBuilder.session.flush()

    for user_id in data.users_ids:
        match: UserChatMatch = UserChatMatch(
            user_id=user_id,
            chat_id=chat.id,
        )
        DBBuilder.session.add(match)
        DBBuilder.session.flush()

        value = 1
        if user_id == user.id:
            value = 0
        unread_count: UnreadCount = UnreadCount(
            user_chat_match_id=match.id,
            value=value,
        )
        DBBuilder.session.add(unread_count)

    make_chat_message_and_add_to_session(
        text=data.text,
        user_id=user.id,
        chat_id=chat.id,
    )

    DBBuilder.session.commit()

    for user_id in data.users_ids:
        result_data = ChatInfoJSONDictMaker.make(chat=chat, user_id=user_id)
        await server.send_to_one_user(
            user_id=user_id,
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

    chat_users: list[User] = chat.users()
    for chat_user in chat_users:
        if chat_user.id == user.id:
            continue

        unread_count: UnreadCount = chat.unread_count_for_user(user_id=chat_user.id)
        unread_count.value += 1

        result_data = NewUnreadCountJSONDictMaker.make(chat_id=chat.id, unread_count=unread_count.value)
        await server.send_to_one_user(
            user_id=chat_user.id,
            message=MessageType.NEW_UNREAD_COUNT.make_json_dict(result_data)
        )

    DBBuilder.session.commit()

    chat_users_ids: list[int] = [chat_user.id for chat_user in chat_users]
    result_data = ChatMessageJSONDictMaker.make(chat_message=chat_message)
    await server.send_to_many_users(
        users_ids=chat_users_ids,
        message=MessageType.NEW_CHAT_MESSAGE.make_json_dict(result_data)
    )


@server.common_handler(MessageType.NEW_CHAT_MESSAGE_TYPING)
@raises(ValidationError, PermissionError, ValueError)
async def new_chat_message_typing(user: User, data: dict) -> None:
    data: ChatIdData = ChatIdData(**data)

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


@server.common_handler(MessageType.CHAT_MESSAGE_WAS_READ)
@raises(ValidationError, ValueError)
async def chat_message_was_read(user: User, data: dict) -> None:
    data: ChatMessageWasReadData = ChatMessageWasReadData(**data)

    chat: Chat = UserChatMatch.chat_if_user_has_access(
        user_id=user.id,
        chat_id=data.chat_id,
    )

    unread_count: UnreadCount = chat.unread_count_for_user(user_id=user.id)

    chat_messages: list[ChatMessage] = chat.unread_messages_for_user(user_id=user.id)
    chat_messages.reverse()

    read_chat_messages_ids: list[int] = []
    senders_ids: set[int] = set()
    for chat_message in chat_messages:
        read_chat_messages_ids.append(chat_message.id)
        senders_ids.add(chat_message.user_id)

        if not chat_message.is_read:
            unread_count.value -= 1
        chat_message.is_read = True

        if chat_message.id == data.chat_message_id:
            break

    if unread_count.value < 0:
        unread_count.value = 0

    if not read_chat_messages_ids:
        return

    DBBuilder.session.commit()

    result_data = NewUnreadCountJSONDictMaker.make(
        chat_id=chat.id,
        unread_count=unread_count.value,
    )
    await server.send_to_one_user(
        user_id=user.id,
        message=MessageType.NEW_UNREAD_COUNT.make_json_dict(result_data),
    )

    for sender_id in senders_ids:
        result_data = ReadChatMessagesJSONDictMaker.make(
            chat_id=chat.id,
            chat_messages_ids=read_chat_messages_ids,
        )
        await server.send_to_one_user(
            user_id=sender_id,
            message=MessageType.READ_CHAT_MESSAGES.make_json_dict(result_data),
        )


if __name__ == '__main__':
    DBBuilder.init_session(url=DB_URL)
    DBBuilder.make_migrations()
    server.run()
