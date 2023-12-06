import asyncio
from websockets import WebSocketServerProtocol, serve, ConnectionClosed  # pip install websockets
import json
from typing import NoReturn
from jwt import decode  # pip install pyjwt

from api.db.models import (
    User,
    ChatMessage,
    UserChatMatch,
    Chat,
    session,
)
from api.json_ import (
    JSONKey,
    JWTAuthWebSocketDataJSONDict,
    WebSocketMessageJSONDict,
    ChatMessageJSONDict,
    JSONDictPreparer,
)
from api.config import (
    HOST,
    WEBSOCKET_PORT as PORT,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
)

# Сюда складываем клиентов, подключённых к серверу в данный момент времени.
# Ключ - ID пользователя `User.id`;
# Значение - список сокетов (список, т.к. человек может быть подключён
# с нескольких вкладок браузера, с телефона и т.д.).
clients: dict[int, list[WebSocketServerProtocol]] = {}


async def main() -> NoReturn:
    """Запускает сервер."""
    print('Serving Websocket server')
    async with serve(ws_handler, HOST, PORT):
        await asyncio.Future()  # run forever


async def wait_data(client: WebSocketServerProtocol) -> dict:
    """Ожидает данные от клиента. При получении сразу преобразует их из JSON -> Python object."""
    return json.loads(await client.recv())


async def dump_and_send(client: WebSocketServerProtocol,
                        data: dict | list,
                        ) -> None:
    """Преобразует `data` в JSON, после чего отправляет данные клиенту."""
    await client.send(json.dumps(data))


async def ws_handler(client: WebSocketServerProtocol) -> None:
    """Обработчик сообщений от клиентов для `serve(ws_handler=...)`."""
    print('New client connected -', client.id)
    try:
        # Сначала авторизуем клиента, после чего добавляем его в `clients`.
        user: User = await wait_auth(client)
    except ConnectionClosed:
        return
    clients.setdefault(user.id, []).append(client)
    print('Client was auth', f'({client.id})')
    try:
        # Запускаем обмен рядовыми сообщениями.
        # При разрыве соединения клиент удаляется из `clients`.
        await start_communication(client, user)
    except ConnectionClosed:
        # Пока досконально не разбирался, но по каким-то причинам элемент может пропасть,
        # из-за чего `.pop(...)` вызовет ошибку.
        try:
            clients[user.id].remove(client)
        except ValueError:
            pass
    print('Connection closed', f'({client.id})')


async def wait_auth(client: WebSocketServerProtocol) -> User:
    """Ожидает валидного авторизующего сообщения от клиента.
    Возвращает объект пользователя.
    """
    while True:
        # Ждём авторизующего сообщения, после чего преобразуем его из JSON -> Python dict
        # и проверяем email + password в БД.
        auth_data: JWTAuthWebSocketDataJSONDict = await wait_data(client)
        auth_token: str = decode(auth_data[JSONKey.JWT_TOKEN],  # type: ignore
                                 key=JWT_SECRET_KEY,
                                 algorithms=[JWT_ALGORITHM])['sub']
        try:
            auth_user: User = User.auth_by_token(auth_token=auth_token)
        except (TypeError, KeyError, ValueError):
            continue
        return auth_user


async def start_communication(client: WebSocketServerProtocol,
                              user: User,
                              ) -> None:
    """Запускает однородный обмен с клиентом чатными сообщениями."""
    while True:
        # Ждём сообщение в какой-нибудь чат.
        message: WebSocketMessageJSONDict = await wait_data(client)
        try:
            if message.get(JSONKey.CHAT_IS_NEW):  # type: ignore
                # Создаём новый чат.
                chat: Chat = Chat.new_with_matches(users_ids=message[JSONKey.USERS_IDS])  # type: ignore
            else:
                # Проверяем доступ к заданному чату.
                chat: Chat = UserChatMatch.chat_if_user_has_access(
                    user_id=user.id,
                    chat_id=message[JSONKey.CHAT_ID],  # type: ignore
                )
            chat_id: int = chat.id
        except (PermissionError, KeyError):
            continue
        # Формируем сообщение для сохранения в БД и дальнейшей рассылки другим клиентам.
        try:
            text: str = message[JSONKey.TEXT]  # type: ignore
            if not text:
                continue
            chat_message: ChatMessage = ChatMessage(
                user_id=user.id,
                chat_id=chat_id,
                text=text,
            )
        except KeyError:
            continue
        # Сохраняем сообщение в БД (не для ФСБ).
        session.add(chat_message)
        session.commit()
        # Отсылаем сообщение всем, кто в данный момент времени подключён к серверу
        # и состоит в текущем чате.
        await send_each(chat_message, message.get(JSONKey.CHAT_IS_NEW, False), chat)  # type: ignore


async def send_each(chat_message: ChatMessage,
                    chat_is_new: bool = False,
                    new_chat: Chat | None = None,
                    ) -> None:
    """Отсылает сообщение каждому клиенту, состоящему в заданном чате, а также подключённому в данный момент
    времени к серверу.
    """
    # Преобразуем объект сообщения в словарь с ключами в стиле lowerCamelCase.
    message_dict: ChatMessageJSONDict = JSONDictPreparer.prepare_chat_message(chat_message)
    # Перебираем пользователей, состоящих в чате.
    for user in UserChatMatch.users_in_chat(chat_message.chat_id):
        try:
            # Если пользователь подключён в данный момент к серверу, то отсылаем ему сообщение.
            if user.id in clients:
                message_dict_for_cur_user = message_dict
                if chat_is_new:
                    message_dict_for_cur_user = {
                        **JSONDictPreparer.prepare_chat_info(chat=new_chat, user_id=user.id),
                        JSONKey.CHAT_IS_NEW: True,
                    }
                for client in clients[user.id]:
                    await dump_and_send(client, message_dict_for_cur_user)
        except ConnectionClosed:
            continue


if __name__ == '__main__':
    asyncio.run(main())
