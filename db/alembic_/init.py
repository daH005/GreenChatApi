from alembic.config import Config
from alembic import command
import logging

from api.config import BASE_DIR, DB_URL

__all__ = (
    'config',
    'make_migrations',
)

logging.getLogger('alembic.runtime.migration').disabled = True

config: Config = Config(BASE_DIR.joinpath('./db/alembic_/alembic.ini'))
config.set_main_option('script_location', str(BASE_DIR.joinpath('./db/alembic_/migrations')))
config.set_main_option('prepend_sys_path', str(BASE_DIR.joinpath('../')))
config.set_main_option('sqlalchemy.url', DB_URL.render_as_string(hide_password=False))


def make_migrations():
    try:
        command.upgrade(config, 'head')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    make_migrations()
