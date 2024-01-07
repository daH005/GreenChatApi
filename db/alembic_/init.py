from alembic.config import Config
from alembic import command

from api.config import BASE_DIR, DB_URL

__all__ = (
    'config',
    'make_migrations',
)

config: Config = Config(BASE_DIR.joinpath('./db/alembic_/alembic.ini'))
config.set_main_option('script_location', str(BASE_DIR.joinpath('./db/alembic_/migrations')))
config.set_main_option('prepend_sys_path', str(BASE_DIR.joinpath('../')))
config.set_main_option('sqlalchemy.url', DB_URL.render_as_string(hide_password=False))


def make_migrations():
    command.upgrade(config, 'head')


if __name__ == '__main__':
    make_migrations()
