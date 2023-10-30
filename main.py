import asyncio
from websockets import WebSocketServerProtocol, serve, ConnectionClosed  # pip install websockets
from uuid import UUID
import json
from typing import TypeAlias

from config import HOST, PORT

# Сюда складываем клиентов, подключённых к чату.
clients: dict[UUID, WebSocketServerProtocol] = {}
MessageType: TypeAlias = dict[str, str]
# FixMe: Сюда временно складываем сообщения. В дальнейшем прикрутим БД.
messages: list[MessageType] = []


async def main() -> None:
    async with serve(ws_handler, HOST, PORT):
        await asyncio.Future()  # run forever


async def ws_handler(client: WebSocketServerProtocol) -> None:
    """Обработчик сообщений от любого клиента."""
    # FixMe: Сделать проверку пользователя. Например, по ключу-токену.
    print('New client connected -', client.id)
    clients[client.id] = client
    await client.send(json.dumps(messages))
    while True:
        try:
            message: MessageType = json.loads(await client.recv())
            # FixMe: Сделать проверку валидности сообщения.
            messages.append(message)
            await send_each(message)
        except ConnectionClosed:
            clients.pop(client.id)
            break
    print('Connection closed', f'({client.id})')


async def send_each(message: MessageType) -> None:
    """Отсылает `message` каждому клиенту. Если вдруг оказывается, что соединение с каким-то
    клиентом оборвано, то он удаляется из `clients`.
    """
    dumped_message: str = json.dumps([message])  # Оборачивание списком обязательно!
    for uuid, client in list(clients.items()):
        try:
            await client.send(dumped_message)
        except ConnectionClosed:
            continue


if __name__ == '__main__':
    asyncio.run(main())
