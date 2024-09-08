from threading import Thread

from api.db.init import init_db
from api.http_.run import run_http
from api.http_.email.run import run_celery
from api.websocket_.run import run_websocket

if __name__ == '__main__':
    init_db()
    Thread(target=run_websocket).start()
    Thread(target=run_celery).start()
    run_http()
