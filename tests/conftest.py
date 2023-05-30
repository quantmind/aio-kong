import aiohttp
import asyncio
import pytest

from kong.client import Kong
from kong.consumers import Consumer
from kong.services import Service

TESTS = ("test", "foo", "pippo")
CONSUMERS = ("an-xxxx-test", "test-xx", "test-yy")


@pytest.fixture(scope="module", autouse=True)
def event_loop():
    """Return an instance of the event loop."""
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture
async def cli() -> Kong:
    session = aiohttp.ClientSession()
    async with Kong(session=session) as cli:
        await cli.delete_all()
        yield cli
        await cli.delete_all()


@pytest.fixture
async def service(cli: Kong) -> Service:
    return await cli.services.create(name="test", host="example.upstream", port=8080)


@pytest.fixture
async def consumer(cli: Kong, service: Service) -> Consumer:
    await service.plugins.create(name="jwt")
    consumer = await cli.consumers.create(username="test-xx")
    return consumer
