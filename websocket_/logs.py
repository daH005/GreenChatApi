from logging import getLogger, basicConfig, INFO

__all__ = (
    'logger',
)

basicConfig(level=INFO)
logger = getLogger(__name__)
