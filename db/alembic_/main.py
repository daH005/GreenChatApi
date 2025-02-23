from sys import argv

from alembic import command
from alembic.config import Config

from config.paths import BASE_DIR
from config.db import DB_URL

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
    action: str
    try:
        action = argv[1]
    except IndexError:
        print('The first argument is absent.')
        exit()

    yes: bool
    try:
        if argv[2] != '--yes':
            print('The second argument is invalid. It must be --yes or nothing.')
            exit()
        yes = True
    except IndexError:
        yes = False

    if not yes:
        answer = input('Have you stopped the app? (write yes): ')
        if answer != 'yes':
            print('The answer is invalid...')
            exit()

    if action.startswith('--revision='):
        message: str = action.split('=')[1]
        if not message:
            print('After the --revision must be some text message.')
            exit()
        make_revision(message)
    elif action == '--migrate':
        make_migrations()
    else:
        print('The first argument is invalid. It must be --revision=<message> or --migrate.')
        exit()
