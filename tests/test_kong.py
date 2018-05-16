import asyncio

import pytest

import aiohttp

from kong.client import Kong


@pytest.fixture(scope='module')
def loop():
    """Return an instance of the event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='module')
async def cli(loop):
    session = aiohttp.ClientSession(loop=loop)
    async with Kong(session=session) as cli:
        yield cli


def test_client(cli):
    assert cli.session
