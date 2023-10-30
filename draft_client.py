# Было решено использовать `websocket`, а не `websocketS` в силу удобства callback'ов.
from websocket import WebSocketApp  # pip install websocket-client
from threading import Thread
import json
import time

from config import URL


def on_open(_) -> None:
    print('Connection opened')


def on_message(_, raw_messages) -> None:
    messages = json.loads(raw_messages)
    for message in messages:
        print('\n', '-' * 5, message['name'] + ':', message['text'], '\n')


def on_close(_) -> None:
    print('Connection closed')


if __name__ == '__main__':
    app: WebSocketApp = WebSocketApp(
        URL,
        on_open=on_open,
        on_message=on_message,
        on_close=on_close,
    )
    thread: Thread = Thread(target=app.run_forever)
    thread.start()
    time.sleep(1)
    name = input('Your name is ')
    while True:
        time.sleep(1)
        text = input('New message - ')
        app.send(json.dumps({'name': name, 'text': text}))
