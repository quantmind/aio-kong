import os

import aiohttp

from .components import Apis, Consumers


class Kong:
    url = os.environ.get('KONG_URL', 'http://127.0.0.1:8001')
    token = None

    def __init__(self, url=None, session=None, full_response=False,
                 timeout=None):
        self.timeout = timeout
        self.url = url or self.url
        self.session = session or aiohttp.ClientSession()
        self.full_response = full_response
        self.apis = Apis(self)
        self.consumers = Consumers(self)

    def __repr__(self):
        return self.url
    __str__ = __repr__

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
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
        kw['timeout'] = timeout or self.timeout
        response = await self.session.request(
            method, url, headers=headers, **kw
        )
        response.raise_for_status()
        if response.status_code == 204:
            return True
        data = response.json()
        return wrap(data) if wrap else data
