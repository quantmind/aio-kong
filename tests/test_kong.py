import os
import pytest
import yaml

from kong.client import KongError


PATH = os.path.dirname(__file__)


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
    await cli.services.create(name='test', host='example.upstream', port=8080)
    c = await cli.services.update('test', host='test.upstream')
    assert c.name == 'test'
    assert c.host == 'test.upstream'


async def test_routes(cli):
    await cli.services.create(name='test', host='example.upstream', port=8080)
    c = await cli.services.get('test')
    routes = await c.routes.get_list()
    assert len(routes) == 0
    route = await c.routes.create(hosts=['example.com'])
    assert route['service']['id'] == c.id


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


async def test_add_certificate(cli):
    c = await cli.certificates.create(
        cert='-----BEGIN CERTIFICATE-----...',
        key='-----BEGIN RSA PRIVATE KEY-----...'
    )
    assert c.id
    assert len(c.data['snis']) == 0
    await cli.certificates.delete(c.id)


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
