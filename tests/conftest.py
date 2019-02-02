import pytest
import asyncio
import aiohttp

from kong.client import Kong


TESTS = ('test', 'foo', 'pippo')
CONSUMERS = ('an-xxxx-test', 'test-xx', 'test-yy')


@pytest.fixture(autouse=True)
def loop():
    """Return an instance of the event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def cli(loop):
    session = aiohttp.ClientSession(loop=loop)
    async with Kong(session=session) as cli:
        await cleanup(cli)
        yield cli
        await cleanup(cli)


@pytest.fixture()
async def service(cli):
    return await cli.services.create(
        name='test', host='example.upstream', port=8080
    )


@pytest.fixture()
async def consumer(cli, service):
    await service.plugins.create(name='jwt')
    consumer = await cli.consumers.create(username='test-xx')
    return consumer


async def cleanup(cli):
    await cli.services.delete_all()
    await cli.consumers.delete_all()
    await cli.plugins.delete_all()
