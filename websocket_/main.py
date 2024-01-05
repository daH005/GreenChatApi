from api.websocket_.base import (
    WebSocketServer,
)
from api.json_ import (
    JSONDictPreparer,
    ChatInitialDataJSONDict,
    ChatMessageJSONDict,
)
from api.db.models import (
    session,
    User,
    Chat,
    UserChatMatch,
)
from api.websocket_.funcs import (
    UserID,
    users_ids_of_chat_by_id,
    make_chat_message_and_add_to_session,
)
from api.websocket_.validation import (
    NewChatMessage,
    NewChat,
)
from api.config import HOST, WEBSOCKET_PORT

server = WebSocketServer(
    host=HOST,
    port=WEBSOCKET_PORT,
)


class WebSocketMessageTypes:

    NEW_CHAT_MESSAGE = 'newChatMessage'
    NEW_CHAT = 'newChat'


@server.handler(WebSocketMessageTypes.NEW_CHAT_MESSAGE)
def new_chat_message(user: User, data: dict) -> tuple[list[UserID], ChatMessageJSONDict]:
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

    return_data = JSONDictPreparer.prepare_chat_message(chat_message=chat_message)
    return users_ids_of_chat_by_id(chat_id=chat.id), return_data


@server.handler(WebSocketMessageTypes.NEW_CHAT)
def new_chat(user: User, data: dict) -> tuple[list[UserID], ChatInitialDataJSONDict]:
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

    return_data = JSONDictPreparer.prepare_chat_info(chat=chat)
    return data.users_ids, return_data


if __name__ == '__main__':
    server.run()
