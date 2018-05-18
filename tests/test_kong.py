import os
import asyncio

import pytest

import yaml

import aiohttp

from kong.client import Kong


PATH = os.path.dirname(__file__)


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
    s = await cli.services.get('test')
    await s.routes.delete_all()
    await s.delete()


def test_client(cli):
    assert cli.session


async def test_create_service(cli):
    c = await cli.services.create(
        name='test', host='example.upstream', port=8080
    )
    assert c.name == 'test'
    assert c.host == 'example.upstream'
    assert c.id


async def test_update_service(cli):
    c = await cli.services.update('test', host='test.upstream')
    assert c.name == 'test'
    assert c.host == 'test.upstream'


async def test_routes(cli):
    c = await cli.services.get('test')
    routes = await c.routes.get_list()
    assert len(routes) == 0
    route = await c.routes.create(hosts=['example.com'])
    assert route['service']['id'] == c.id


async def test_json(cli):
    with open(os.path.join(PATH, 'test.yml')) as fp:
        manifest = yaml.load(fp)
    await cli.apply_json(manifest)
