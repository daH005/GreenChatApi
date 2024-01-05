from base64 import b64decode, b64encode
from typing import Final

__all__ = (
    'make_auth_token',
    'decode_auth_token',
    'USERNAME_AND_PASSWORD_SEP',
)

USERNAME_AND_PASSWORD_SEP: Final[str] = '---c2VwYXJhdG9y---'


def make_auth_token(username: str,
                    password: str,
                    ) -> str:
    full_str: str = username + USERNAME_AND_PASSWORD_SEP + password
    return b64encode(full_str.encode()).decode()


def decode_auth_token(auth_token: str) -> tuple[str, str]:
    decoded_str: str = b64decode(auth_token.encode()).decode()
    username, password = decoded_str.split(USERNAME_AND_PASSWORD_SEP)
    return username, password


if __name__ == '__main__':
    token = make_auth_token('dan005', 'passmypass123')
    print(token)
    print(decode_auth_token(token))
