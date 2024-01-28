from pydantic import ValidationError

from api.websocket_.base import (
    WebSocketServer,
    TYPE_KEY,
    DATA_KEY,
)
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
from api.websocket_.funcs import (
    users_ids_of_chat_by_id,
    make_chat_message_and_add_to_session,
)
from api.websocket_.validation import (
    NewChat,
    NewChatMessage,
    NewChatTypingMessage,
)
from api.config import HOST, WEBSOCKET_PORT
from api.hinting import raises

server = WebSocketServer(
    host=HOST,
    port=WEBSOCKET_PORT,
)


class MessageTypes:

    NEW_CHAT = 'newChat'
    NEW_CHAT_MESSAGE = 'newChatMessage'
    NEW_CHAT_MESSAGE_TYPING = 'newChatMessageTyping'


@server.handler(MessageTypes.NEW_CHAT)
@raises(ValidationError, ValueError)
async def new_chat(user: User, data: dict) -> None:
    data: NewChat = NewChat(**data)

    if user.id not in data.users_ids:
        raise ValueError

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
        message={
            TYPE_KEY: MessageTypes.NEW_CHAT,
            DATA_KEY: result_data,
        },
    )


@server.handler(MessageTypes.NEW_CHAT_MESSAGE)
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
        message={
            TYPE_KEY: MessageTypes.NEW_CHAT_MESSAGE,
            DATA_KEY: result_data,
        },
    )


@server.handler(MessageTypes.NEW_CHAT_MESSAGE_TYPING)
@raises(ValidationError, PermissionError, ValueError)
async def new_chat_message_typing(user: User, data: dict) -> None:
    data: NewChatTypingMessage = NewChatTypingMessage(**data)

    # think about dry...
    chat: Chat = UserChatMatch.chat_if_user_has_access(
        user_id=user.id,
        chat_id=data.chat_id,
    )

    ids = users_ids_of_chat_by_id(chat_id=chat.id)
    ids.remove(user.id)

    result_data = ChatMessageTypingJSONDictMaker.make(chat_id=chat.id, user=user)
    await server.send_to_many_users(
        users_ids=ids,
        message={
            TYPE_KEY: MessageTypes.NEW_CHAT_MESSAGE_TYPING,
            DATA_KEY: result_data,
        },
    )


if __name__ == '__main__':
    make_migrations()
    server.run()
