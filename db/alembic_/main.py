from alembic import command
from alembic.config import Config

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


def make_revision(message: str) -> None:
    try:
        command.revision(config, message, autogenerate=True)
    except Exception as e:
        print(e)


def make_migrations() -> None:
    try:
        command.upgrade(config, 'head')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    answer = input('Have you stopped the app? (write yes): ')
    if answer != 'yes':
        print('Invalid')
        exit()

    enter = input('Input "1" for revision, "2" for migrations: ')
    if enter == '1':
        make_revision(input('Enter your revision message: '))
    elif enter == '2':
        make_migrations()
    else:
        print('Invalid')
        exit()
