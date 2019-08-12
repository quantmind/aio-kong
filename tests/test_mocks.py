from typing import Dict, Tuple

import aiohttp
from kong.client import Kong


async def async_mock(*args, **kwargs) -> Tuple:
    return (args, kwargs)


async def async_passthrough(response) -> Dict:
    return response[1]


async def test_request_kwargs(loop):
    session = aiohttp.ClientSession(loop=loop)
    cli = Kong(session=session, request_kwargs=dict(ssl=False))
    cli.session.request = async_mock
    kwargs = await cli.execute("...", callback=async_passthrough, bla="foo")
    kwargs.pop("headers")
    assert kwargs == dict(ssl=False, bla="foo")
