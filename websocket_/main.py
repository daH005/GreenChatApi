import asyncio
from websockets import WebSocketServerProtocol, serve, ConnectionClosed  # pip install websockets
import json
from pydantic import ValidationError  # pip install pydantic

from config import HOST, PORT
from api.websocket_.validation import ChatMessage, AuthMessage
# FixMe: Скорректировать после привязки БД.
from api.db import users, chats

# Сюда складываем клиентов, подключённых к серверу.
# Ключ - ID пользователя;
# Значение - сокет.
clients: dict[int, WebSocketServerProtocol] = {}


async def main() -> None:
    print('Serving Websocket server')
    async with serve(ws_handler, HOST, PORT):
        await asyncio.Future()  # run forever


async def ws_handler(client: WebSocketServerProtocol) -> None:
    """Обработчик сообщений от клиентов для `serve(ws_handler=...)`."""
    # Сначала авторизуем пользователя, после чего добавляем клиента в `clients`.
    user_id: int = await wait_auth(client)
    clients[user_id] = client
    print('New client connected -', client.id)
    try:
        # Запускаем обмен рядовыми сообщениями.
        # При разрыве соединения клиент удаляется из `clients`.
        await start_communication(client)
    except ConnectionClosed:
        clients.pop(user_id)
    print('Connection closed', f'({client.id})')


async def wait_auth(client: WebSocketServerProtocol) -> int:
    """Ожидает валидного авторизующего сообщения от клиента.
    Возвращает ID пользователя.
    """
    while True:
        try:
            # Ждём авторизующего сообщения, после чего преобразуем его из JSON -> Python dict,
            # проведя валидацию.
            auth_message: AuthMessage = AuthMessage.model_validate_json(await client.recv())
        except ValidationError:
            continue
        return auth_message.user_id


async def start_communication(client: WebSocketServerProtocol) -> None:
    """Запускает стабильный обмен сообщениями с клиентом."""
    while True:
        try:
            # Ждём сообщения, после чего преобразуем его из JSON -> Python dict,
            # проведя валидацию.
            chat_message: ChatMessage = ChatMessage.model_validate_json(await client.recv())
        except ValidationError:
            continue
        # Сохраняем сообщение в БД для ФСБ.
        # FixMe: Скорректировать после привязки БД.
        chats[chat_message.chat_id]['messages'].append(chat_message)
        await send_each(chat_message)


async def send_each(chat_message: ChatMessage) -> None:
    """Отсылает сообщение каждому клиенту, состоящему в заданном чате, а также подключённому в данный момент
    времени к серверу.
    """
    # Добавляем имя пользователя к сообщению, после чего преобразуем его в JSON.
    dumped_message: str = json.dumps([dict(
        # FixMe: Скорректировать после привязки БД.
        name=users[chat_message.user_id]['name'],
        **chat_message.model_dump(by_alias=True)
    )])
    # Перебираем пользователей, состоящих в чате.
    # FixMe: Скорректировать после привязки БД.
    for user_id in chats[chat_message.chat_id]['users_ids']:
        try:
            # Если пользователь подключён к серверу, то отсылаем ему сообщение.
            if user_id in clients:
                await clients[user_id].send(dumped_message)
        except ConnectionClosed:
            continue


if __name__ == '__main__':
    asyncio.run(main())
