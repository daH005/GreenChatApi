from api.config import HOST, HTTP_PORT as PORT, DEBUG, DB_URL
from api.db.builder import DBBuilder
from api.ssl_context import get_ssl_context
from api.http_.app import app
from api.http_.app_preparing import init_all_dependencies

if __name__ == '__main__':
    init_all_dependencies()
    DBBuilder.init_session(url=DB_URL)
    DBBuilder.make_migrations()
    app.run(HOST, PORT, debug=DEBUG, ssl_context=get_ssl_context())
