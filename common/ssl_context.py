from pathlib import Path
from ssl import SSLContext, create_default_context, Purpose

__all__ = (
    'create_ssl_context',
)


def create_ssl_context(certfile: Path,
                       keyfile: Path,
                       ) -> SSLContext | None:
    ssl_context = create_default_context(Purpose.CLIENT_AUTH)
    try:
        ssl_context.load_cert_chain(certfile, keyfile)
    except FileNotFoundError:
        return
    return ssl_context
