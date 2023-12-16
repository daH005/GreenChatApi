import asyncio
from websockets import WebSocketServerProtocol, serve, ConnectionClosed  # pip install websockets
import json
from typing import NoReturn, Final
from jwt import decode  # pip install pyjwt
from enum import StrEnum

from api.db.models import (
    User,
    ChatMessage,
    UserChatMatch,
    Chat,
    session,
)
from api.json_ import (
    JSONKey,
    WebSocketMessageJSONDict,
    JSONDictPreparer,
)
from api.config import (
    HOST,
    WEBSOCKET_PORT as PORT,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
)


class MessageType(StrEnum):
    """Перечисление всевозможных видов сообщений, с которыми работает веб-сокет."""

    AUTH = 'auth'
    NEW_CHAT_MESSAGE = 'newChatMessage'
    NEW_CHAT = 'newChat'


# Сюда складываем клиентов, подключённых к серверу в данный момент времени.
# Ключ - ID пользователя `User.id`;
# Значение - список сокетов (список, т.к. человек может быть подключён
# с нескольких вкладок браузера, с телефона и т.д.).
clients: dict[int, list[WebSocketServerProtocol]] = {}
# Максимальная длина текстового сообщения.
TEXT_MAX_LENGTH: Final[int] = 10_000


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
    await client.send(json.dumps(data, ensure_ascii=False))


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
        # Запускаем обмен сообщениями - в чаты, на добавление чатов, изменение / удаление сообщений и т.д.
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
    Возвращает объект `User`.
    """
    while True:
        # Ждём авторизующего сообщения, после чего преобразуем его из JSON -> Python dict
        # и проверяем валидность JWT-токена.
        message: WebSocketMessageJSONDict = await wait_data(client)
        try:
            if message[JSONKey.TYPE] != MessageType.AUTH:  # type: ignore
                continue
            auth_token: str = decode(
                message[JSONKey.DATA][JSONKey.JWT_TOKEN],  # type: ignore
                key=JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM],
            )['sub']
            auth_user: User = User.auth_by_token(auth_token=auth_token)
        except (TypeError, KeyError, ValueError):
            continue
        return auth_user


async def start_communication(client: WebSocketServerProtocol,
                              user: User,
                              ) -> None:
    """Запускает обмен основными сообщениями с клиентом."""
    while True:
        # Ждём какое-нибудь сообщение. После чего смотрим ключ 'type' и выполняем нужное действие.
        message: WebSocketMessageJSONDict = await wait_data(client)
        try:
            if message[JSONKey.TYPE] == MessageType.NEW_CHAT:  # type: ignore
                # Проверка: пользователь не может создать чат между другими людьми, но не с собой.
                users_ids = message[JSONKey.DATA][JSONKey.USERS_IDS]  # type: ignore
                if user.id not in users_ids:
                    continue
                # Попробуем найти чат перед его созданием.
                # Если окажется, что чат уже существует, то модифицируем текущий "ивент",
                # сделав его `MessageType.NEW_CHAT_MESSAGE`.
                try:
                    chat: Chat = UserChatMatch.find_private_chat(*users_ids)
                    message[JSONKey.TYPE] = MessageType.NEW_CHAT_MESSAGE  # type: ignore
                except ValueError:
                    chat: Chat = Chat.new_with_matches(users_ids=users_ids)
            elif message[JSONKey.TYPE] == MessageType.NEW_CHAT_MESSAGE:  # type: ignore
                # Проверяем доступ к заданному чату.
                chat: Chat = UserChatMatch.chat_if_user_has_access(
                    user_id=user.id,
                    chat_id=message[JSONKey.DATA][JSONKey.CHAT_ID],  # type: ignore
                )
            else:
                continue
        # Пояснение каждого исключения:
        # 1. `PermissionError` - при попытке получить не свой чат.
        # 2. `KeyError` - невалидный JSON.
        # 3. `TypeError` - если длина `users_ids` больше 2-х.
        except (PermissionError, KeyError, TypeError):
            continue
        # Формируем сообщение для чата.
        try:
            # Обрезаем сообщение. Если оно гигантских размеров, то это гарантированно спам / флуд.
            text: str = message[JSONKey.DATA][JSONKey.TEXT][:TEXT_MAX_LENGTH]  # type: ignore
            if not text:
                continue
            chat_message: ChatMessage = ChatMessage(
                user_id=user.id,
                chat_id=chat.id,
                text=text,
            )
        except KeyError:
            continue
        # Сохраняем сообщение в БД (не для ФСБ).
        session.add(chat_message)
        session.commit()
        # Отсылаем сообщение всем, кому оно адресовано, а также в данный момент времени подключённому к серверу.
        await send_each(
            chat_message=chat_message,
            message_type=message[JSONKey.TYPE],  # type: ignore
            chat=chat,
        )


async def send_each(chat_message: ChatMessage,
                    message_type: MessageType,
                    chat: Chat | None = None,
                    ) -> None:
    """Отсылает сообщение каждому клиенту, кому оно адресовано, а также подключённому в данный момент."""
    # Начинаем составлять ответное сообщение.
    answer_message: WebSocketMessageJSONDict = {
        JSONKey.TYPE: message_type,
        JSONKey.DATA: {},
    }
    # Если тип сообщения - создание нового сообщения в чате, то сразу определяем одинаковые для всех получателей
    # данные.
    if message_type == MessageType.NEW_CHAT_MESSAGE:
        answer_message[JSONKey.DATA] = JSONDictPreparer.prepare_chat_message(chat_message=chat_message)  # type: ignore
    # Перебираем пользователей, состоящих в чате.
    for user in UserChatMatch.users_in_chat(chat_message.chat_id):
        try:
            # Если пользователь подключён в данный момент к серверу, то мы отошлём ему сообщение.
            if user.id in clients:
                cur_message = answer_message
                # Если тип сообщения - создание нового чата, то определяем конкретные данные для текущего получателя.
                if message_type == MessageType.NEW_CHAT:
                    cur_message[JSONKey.DATA] = JSONDictPreparer.prepare_chat_info(chat=chat,  # type: ignore
                                                                                   user_id=user.id)
                for client in clients[user.id]:
                    await dump_and_send(client, cur_message)
        except ConnectionClosed:
            continue


if __name__ == '__main__':
    asyncio.run(main())
