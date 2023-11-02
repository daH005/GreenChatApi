import asyncio
from websockets import WebSocketServerProtocol, serve, ConnectionClosed  # pip install websockets
from uuid import UUID
import json
from typing import TypeAlias
from pydantic import BaseModel, ValidationError, Field

from config import HOST, PORT


class ChatMessage(BaseModel):
    user_id: int = Field(alias='userId')
    chat_id: int = Field(alias='chatId')
    text: str


class AuthMessage(BaseModel):
    user_id: int = Field(alias='userId')


# Сюда складываем клиентов, подключённых к чату.
clients: dict[int, WebSocketServerProtocol] = {}
MessageDictType: TypeAlias = dict[str, str]
# FixMe: Сюда временно складываем сообщения. В дальнейшем прикрутим БД.
chats: list[dict] = [
    # 0
    {
        'messages': [],
        'users_ids': [0, 1],
    },
    # 1
    {
        'messages': [],
        'users_ids': [0, 1],
    },
]
users: list[dict[str, str]] = [
    {
        'name': 'Danil',
    },
    {
        'name': 'Ivan'
    },
]


async def main() -> None:
    async with serve(ws_handler, HOST, PORT):
        await asyncio.Future()  # run forever


async def ws_handler(client: WebSocketServerProtocol) -> None:
    """Обработчик сообщений от любого клиента."""
    # FixMe: Сделать проверку пользователя. Например, по ключу-токену.
    auth_message: AuthMessage
    while True:
        try:
            auth_message: AuthMessage = AuthMessage(**json.loads(await client.recv()))
        except ValidationError:
            continue
        clients[auth_message.user_id] = client
        break

    print('New client connected -', client.id)

    # await client.send(json.dumps(messages))

    while True:
        try:
            try:
                chat_message: ChatMessage = ChatMessage(**json.loads(await client.recv()))
            except ValidationError:
                continue
            chats[chat_message.chat_id]['messages'].append(chat_message)
            await send_each(chat_message)
        except ConnectionClosed:
            clients.pop(auth_message.user_id)  # noqa
            break
    print('Connection closed', f'({client.id})')


async def send_each(chat_message: ChatMessage) -> None:
    """Отсылает `message` каждому клиенту. Если вдруг оказывается, что соединение с каким-то
    клиентом оборвано, то он удаляется из `clients`.
    """
    dumped_message: str = json.dumps([{
        **chat_message.model_dump(by_alias=True),
        'name': users[chat_message.user_id]['name'],
    }])
    for user_id in chats[chat_message.chat_id]['users_ids']:
        try:
            if user_id in clients:
                await clients[user_id].send(dumped_message)
        except ConnectionClosed:
            continue


if __name__ == '__main__':
    asyncio.run(main())
