from pathlib import Path
from ssl import SSLContext, create_default_context, Purpose

from api.config import BASE_DIR

__all__ = (
    'get_ssl_context',
)


def get_ssl_context() -> SSLContext | None:
    ssl_path: Path = BASE_DIR.joinpath('ssl_')
    if not ssl_path.exists():
        return

    ssl_context = create_default_context(Purpose.CLIENT_AUTH)
    try:
        ssl_context.load_cert_chain(
            certfile=ssl_path.joinpath('certificate.crt'),
            keyfile=ssl_path.joinpath('private.key'),
        )
    except FileNotFoundError:
        return

    return ssl_context
