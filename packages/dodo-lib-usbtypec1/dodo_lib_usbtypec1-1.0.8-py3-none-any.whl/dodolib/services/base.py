import httpx

from ..utils import env_vars, exceptions

__all__ = (
    'BaseHTTPService',
)


class BaseHTTPService:
    service_name: str = None

    def __init__(self, base_url: str | None = None, client: httpx.AsyncClient | None = None):
        if base_url is None:
            base_url = self.get_base_url_from_env_var()
        self._client = client
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=base_url, timeout=120)

    @classmethod
    def get_base_url_from_env_var(cls) -> str:
        return env_vars.get_base_url(cls.service_name)

    async def close(self):
        if not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def ping(self):
        response = await self._client.get('/ping')
        if response.is_error:
            raise exceptions.HTTPAPIConnectionError
