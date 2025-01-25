from threading import Thread

from http_.run import run_http_wsgi as run_http
from http_.users.email.run import run_celery
from websocket_.run import run_websocket

if __name__ == '__main__':
    for func in (run_websocket, run_http, run_celery):
        Thread(target=func).start()

    while True:
        pass
