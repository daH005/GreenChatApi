from logging import getLogger, basicConfig, INFO

__all__ = (
    'logger',
    'init_logs',
)

logger = getLogger(__name__)


def init_logs() -> None:
    basicConfig(level=INFO)
    logger.setLevel(level=INFO)
    logger.disabled = False


init_logs()
