import pytest
from typing import Final

from api.db.encryption import make_auth_token, decode_auth_token, USERNAME_AND_PASSWORD_SEP

ARGS_NAMES: Final[tuple[str, str]] = ('username', 'password')
DATA_FOR_TESTS: Final[list[tuple[str, str]]] = [
    ('danil', 'mypass'),
    ('danila', 'passsss'),  # noqa
    ('ivan', '9090909091231---'),
]


@pytest.mark.parametrize(ARGS_NAMES, DATA_FOR_TESTS)
def test_positive_encrypts(username: str, password: str) -> None:
    token = make_auth_token(username, password)
    assert token != username
    assert token != password
    assert token != username + ' ' + password
    assert token != username + USERNAME_AND_PASSWORD_SEP + password


@pytest.mark.parametrize(ARGS_NAMES, DATA_FOR_TESTS)
def test_positive_correctly_decrypts(username: str, password: str) -> None:
    token = make_auth_token(username, password)
    d_username, d_password = decode_auth_token(token)
    assert username == d_username
    assert d_password == d_password


def test_positive_no_repeats() -> None:
    tokens = []
    for sub_data in DATA_FOR_TESTS:
        tokens.append(make_auth_token(*sub_data))
    assert len(tokens) == len(set(tokens))
