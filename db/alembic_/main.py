from alembic.config import Config
from alembic import command

from config import BASE_DIR, DB_URL

__all__ = (
    'config',
    'make_revision',
    'make_migrations',
)

config: Config = Config(
    file_=BASE_DIR.joinpath('./db/alembic_/alembic.ini'),
)
config.set_main_option(
    name='script_location',
    value=str(BASE_DIR.joinpath('./db/alembic_/migrations'))
)
config.set_main_option(
    name='prepend_sys_path',
    value=str(BASE_DIR.joinpath('../'))
)
config.set_main_option(
    name='sqlalchemy.url',
    value=DB_URL.render_as_string(hide_password=False)
)


def make_revision(message: str):
    try:
        command.revision(config, message, autogenerate=True)
    except Exception as e:
        print(e)


def make_migrations():
    try:
        command.upgrade(config, 'head')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    make_revision(input('Enter your revision message - '))
    make_migrations()
