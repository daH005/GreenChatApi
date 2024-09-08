from api.config import HOST, HTTP_PORT as PORT, DEBUG, DB_URL
from api.db.builder import db_builder
from api.common.ssl_context import get_ssl_context
from api.http_.app import app
from api.http_.app_preparing import init_all_dependencies

if __name__ == '__main__':
    init_all_dependencies()
    db_builder.init_session(url=DB_URL)
    db_builder.make_migrations()
    app.run(HOST, PORT, debug=DEBUG, ssl_context=get_ssl_context())
