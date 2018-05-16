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
        await cleanup(cli)


async def cleanup(cli):
    await cli.services.delete('test')


def test_client(cli):
    assert cli.session


async def test_create_service(cli):
    c = await cli.services.create(name='test', host='example.com', port=8080)
    assert c.name == 'test'
    assert c.host == 'example.com'
    assert c.id


async def test_update_service(cli):
    c = await cli.services.update('test', host='test.com')
    assert c.name == 'test'
    assert c.host == 'test.com'
