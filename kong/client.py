import os
import json

import aiohttp

from .components import KongError, KongResponseError
from .services import Services
from .plugins import Plugins
from .consumers import Consumers
from .certificates import Certificates


__all__ = [
    'Kong',
    'KongError',
    'KongResponseError'
]


class Kong:
    url = os.environ.get('KONG_URL', 'http://127.0.0.1:8001')

    def __init__(self, url: str=None, session: object=None) -> None:
        self.url = url or self.url
        self.session = session or aiohttp.ClientSession()
        self.services = Services(self)
        self.plugins = Plugins(self)
        self.consumers = Consumers(self)
        self.certificates = Certificates(self)

    def __repr__(self) -> str:
        return self.url
    __str__ = __repr__

    @property
    def cli(self):
        return self

    async def close(self) -> None:
        await self.session.close()

    async def __aenter__(self) -> object:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def execute(self, url, method=None, headers=None,
                      callback=None, wrap=None, timeout=None, skip_error=None,
                      **kw):
        method = method or 'GET'
        headers = headers or {}
        headers['Accept'] = 'application/json, text/*; q=0.5'
        response = await self.session.request(
            method, url, headers=headers, **kw
        )
        if callback:
            return await callback(response)
        if response.status == 204:
            return True
        data = await response.json()
        if response.status >= 400:
            raise KongResponseError(response, json.dumps(data, indent=4))
        response.raise_for_status()
        return wrap(data) if wrap else data

    async def apply_json(self, config):
        if not isinstance(config, dict):
            raise KongError('Expected a dict got %s' % type(config).__name__)
        result = {}
        for name, data in config.items():
            if not isinstance(data, list):
                data = [data]
            o = getattr(self, name)
            if not o:
                raise KongError('Kong object %s not available' % name)
            result[name] = await o.apply_json(data)
        return result
