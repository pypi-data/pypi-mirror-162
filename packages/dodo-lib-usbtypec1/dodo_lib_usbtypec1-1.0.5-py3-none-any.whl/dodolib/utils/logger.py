import logging

__all__ = (
    'logger',
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(name='dodolib')
