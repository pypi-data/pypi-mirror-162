import os
from functools import lru_cache

from . import exceptions
from .logger import logger

try:
    from dotenv import load_dotenv
except ImportError as error:
    logger.critical('Package `python-dotenv` is missing.'
                    ' Install it with `pip install python-dotenv`'
                    ' or `poetry add python-dotenv`')
    raise error

__all__ = (
    'get_base_url',
)

load_dotenv()


@lru_cache(maxsize=3)
def get_base_url(service_name: str) -> str:
    if service_name is None:
        raise ValueError('Service name must not be None')
    env_var_name = f'{service_name}_BASE_URL'
    base_url = os.getenv(env_var_name)
    if base_url is None:
        raise exceptions.NoEnvVarSetUpError(env_var_name=env_var_name)
    return base_url.removesuffix('/')
