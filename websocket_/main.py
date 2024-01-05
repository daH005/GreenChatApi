from api.websocket_.base import (
    WebSocketServer,
    HandlerFuncReturnT,
)
from api.json_ import (
    JSONDictPreparer,
)
from api.db.models import (
    session,
    User,
    Chat,
    ChatMessage,
    UserChatMatch,
)
from api.websocket_.funcs import (
    clear_text_message,
    users_ids_of_chat_by_id,
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
def new_chat_message(user: User,
                     data: dict,
                     ) -> HandlerFuncReturnT:
    data = NewChatMessage(**data)

    chat: Chat = UserChatMatch.chat_if_user_has_access(
        user_id=user.id,
        chat_id=data.chat_id,
    )

    chat_message: ChatMessage = ChatMessage(
        user_id=user.id,
        chat_id=chat.id,
        text=clear_text_message(text=data.text),
    )
    session.add(chat_message)
    session.commit()

    return_data = JSONDictPreparer.prepare_chat_message(chat_message=chat_message)
    return users_ids_of_chat_by_id(chat_id=chat.id), return_data


@server.handler(WebSocketMessageTypes.NEW_CHAT)
def new_chat(user: User,
             data: dict,
             ) -> HandlerFuncReturnT:
    data = NewChat(**data)

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

    matches = []
    for id_ in data.users_ids:
        match = UserChatMatch(
            user_id=id_,
            chat_id=chat.id,
        )
        matches.append(match)

    session.add_all([chat, *matches])
    session.commit()

    return_data = JSONDictPreparer.prepare_chat_info(chat=chat)
    return data.users_ids, return_data


if __name__ == '__main__':
    server.run()
