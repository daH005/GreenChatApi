import pytest
from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from mock_alchemy.comparison import mock

from api.db import models
from api.db.models import *

_TEST_PASSWORDS = [
    '901239-18fsdgd0sf7g===23421341',  # noqa
    '324-fdsg-df-g-345345',  # noqa
]
_TEST_USERS = [
    User.new_by_password(
        username='dan005',
        first_name='Данил',
        last_name='Шевелёв',
        email='danil.shevelev.2004@mail.ru',
        password=_TEST_PASSWORDS[0],  # noqa
    ),
    User.new_by_password(
        username='skeletonik',  # noqa
        first_name='Данила',
        last_name='Крохалев',
        email='test_email.2003@mail.ru',
        password=_TEST_PASSWORDS[1],  # noqa
    ),
]
mock_session: UnifiedAlchemyMagicMock = UnifiedAlchemyMagicMock(data=[
    # Настраиваем тестовые фильтрации по токену, чтобы они выдавали ожидаемых пользователей.
    (
        [mock.call.filter(User.auth_token == _TEST_USERS[0].auth_token)],
        [_TEST_USERS[0]]
     ),
    (
        [mock.call.filter(User.auth_token == _TEST_USERS[1].auth_token)],
        [_TEST_USERS[1]]
    ),
])


def setup() -> None:
    models.session = mock_session
    mock_session.add_all(_TEST_USERS)
    mock_session.commit()


@pytest.mark.parametrize('user', _TEST_USERS)
def test_user_creating_with_auth_token_generating_and_no_password_saving(user: User) -> None:
    """Тест: у созданных пользователей должен быть токен авторизации и не
    должно быть чистого пароля.
    """
    assert hasattr(user, 'auth_token')
    assert not hasattr(user, 'password')


@pytest.mark.parametrize(('user', 'password'), zip(_TEST_USERS, _TEST_PASSWORDS))
def test_auth_user_by_username_and_password(user: User,
                                            password: str,
                                            ) -> None:
    """Тест: авторизация по логину и паролю должна работать.
    """
    assert User.auth_by_username_and_password(user.username, password) == user


@pytest.mark.parametrize('user', _TEST_USERS)
def test_auth_user_by_token(user: User) -> None:
    """Тест: авторизация по токену должна работать.
    """
    assert User.auth_by_token(user.auth_token) == user
