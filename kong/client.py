import os
import json

import aiohttp

from .components import Services, Consumers, KongError


class Kong:
    url = os.environ.get('KONG_URL', 'http://127.0.0.1:8001')
    token = None

    def __init__(self, url: str=None, session: object=None) -> None:
        self.url = url or self.url
        self.session = session or aiohttp.ClientSession()
        self.services = Services(self)
        self.consumers = Consumers(self)

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

    async def execute(self, url, method=None, headers=None, token=None,
                      callback=None, wrap=None, timeout=None, skip_error=None,
                      **kw):
        method = method or 'GET'
        headers = headers or {}
        token = token or self.token
        if token:
            headers['Authorization'] = 'Bearer %s' % token
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
            raise KongError(response, json.dumps(data, indent=4))
        response.raise_for_status()
        return wrap(data) if wrap else data

    async def apply_json(self, srv):
        if not isinstance(srv, dict):
            raise TypeError('Expected a dict got %s' % type(srv).__name__)
        for name, data in srv.items():
            if not isinstance(data, list):
                data = [data]
            o = getattr(self, name)
            if not o:
                raise ValueError('Kong object %s not available' % name)
            for entry in data:
                if not isinstance(entry, dict):
                    raise TypeError(
                        'Expected a dict got %s' % type(entry).__name__
                    )
                await o.apply_json(entry)
