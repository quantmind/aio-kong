import pytest
import asyncio
import aiohttp

from kong.client import Kong, KongError


TESTS = ('test', 'foo', 'pippo')
CONSUMERS = ('an-xxxx-test',)


@pytest.fixture(scope='session')
def loop():
    """Return an instance of the event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def cli(loop):
    session = aiohttp.ClientSession(loop=loop)
    async with Kong(session=session) as cli:
        yield cli
        await cleanup(cli)


async def cleanup(cli):
    for name in TESTS:
        try:
            await cli.services.remove(name)
        except KongError as exc:
            if not exc.status == 404:
                raise
    for consumer in CONSUMERS:
        try:
            await cli.consumers.delete(name)
        except KongError as exc:
            if not exc.status == 404:
                raise
