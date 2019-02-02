import os
import pytest
import yaml

from kong.client import KongError


PATH = os.path.dirname(__file__)


async def test_json(cli):
    with open(os.path.join(PATH, 'test.yaml')) as fp:
        manifest = yaml.load(fp)
    await cli.apply_json(manifest)
    srv = await cli.services.get('foo')
    routes = await srv.routes.get_list()
    assert len(routes) == 2
    #
    # check plugins
    plugins = await srv.plugins.get_list()
    assert len(plugins) == 2


async def test_json2(cli):
    with open(os.path.join(PATH, 'test2.yaml')) as fp:
        manifest = yaml.load(fp)
    await cli.apply_json(manifest)
    srv = await cli.services.get('foo')
    routes = await srv.routes.get_list()
    assert len(routes) == 1
    #
    # check plugins
    plugins = await srv.plugins.get_list()
    assert len(plugins) == 2


async def test_hedge_cases(cli):
    with pytest.raises(KongError):
        await cli.apply_json([])

    with pytest.raises(KongError):
        with open(os.path.join(PATH, 'test3.yaml')) as fp:
            await cli.apply_json(yaml.load(fp))

    assert str(cli) == cli.url


async def test_json_plugins(cli):
    with open(os.path.join(PATH, 'test4.yaml')) as fp:
        await cli.apply_json(yaml.load(fp))


async def test_json_route_plugins(cli):
    with open(os.path.join(PATH, 'test6.yaml')) as fp:
        await cli.apply_json(yaml.load(fp))
    with open(os.path.join(PATH, 'test6.yaml')) as fp:
        await cli.apply_json(yaml.load(fp))
    srv = await cli.services.get('pippo')
    plugins = await srv.plugins.get_list()
    assert len(plugins) == 1
    routes = await srv.routes.get_list()
    assert len(routes) == 1
    plugins = await routes[0].plugins.get_list()
    assert len(plugins) == 3
    cs = await cli.consumers.get('an-xxxx-test')
    acls = await cs.acls.get_list()
    assert len(acls) == 2

    with open(os.path.join(PATH, 'test61.yaml')) as fp:
        await cli.apply_json(yaml.load(fp))
    srv = await cli.services.get('pippo')
    plugins = await srv.plugins.get_list()
    assert len(plugins) == 0
    routes = await srv.routes.get_list()
    assert len(routes) == 1
    plugins = await routes[0].plugins.get_list()
    assert len(plugins) == 1
    cs = await cli.consumers.get('an-xxxx-test')
    acls = await cs.acls.get_list()
    assert len(acls) == 1


async def test_ensure_remove(cli):
    with open(os.path.join(PATH, 'test6.yaml')) as fp:
        await cli.apply_json(yaml.load(fp))
    assert await cli.services.has('pippo') is True
    with open(os.path.join(PATH, 'test7.yaml')) as fp:
        await cli.apply_json(yaml.load(fp))
    assert await cli.services.has('pippo') is False
    with open(os.path.join(PATH, 'test7.yaml')) as fp:
        await cli.apply_json(yaml.load(fp))
    assert await cli.services.has('pippo') is False
