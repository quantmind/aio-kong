import pytest
import asyncio
import aiohttp

from kong.client import Kong, KongError


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
    for name in TESTS:
        try:
            await cli.services.remove(name)
        except KongError as exc:
            if not exc.status == 404:
                raise
    for name in CONSUMERS:
        try:
            await cli.consumers.delete(name)
        except KongError as exc:
            if not exc.status == 404:
                raise
