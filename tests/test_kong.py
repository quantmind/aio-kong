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
    srv = await cli.services.get('pippo')
    plugins = await srv.plugins.get_list()
    assert len(plugins) == 1
    routes = await srv.routes.get_list()
    assert len(routes) == 1
    plugins = await routes[0].plugins.get_list()
    assert len(plugins) == 3
    cs = await cli.consumers.get('an-xxxx-test')
    acls = await cs.acls()
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
    acls = await cs.acls()
    assert len(acls) == 1


async def test_snis(cli):
    c1 = await cli.certificates.create(
        cert='-----BEGIN CERTIFICATE-----...',
        key='-----BEGIN RSA PRIVATE KEY-----...'
    )
    c2 = await cli.certificates.create(
        cert='-----BEGIN CERTIFICATE-----...',
        key='-----BEGIN RSA PRIVATE KEY-----...'
    )
    config = {
        'snis': [
            {
                'name': 'a1.example.com',
                'ssl_certificate_id': c1['id'],
            },
            {
                'name': 'a2.example.com',
                'ssl_certificate_id': c2['id'],
            },
        ]
    }
    resp = await cli.apply_json(config)
    snis = resp['snis']

    # CREATE
    for sni in snis:
        sni.pop('created_at')
    assert snis == config['snis']

    # UPDATE
    config['snis'][0]['ssl_certificate_id'] = c2['id']
    config['snis'][1]['ssl_certificate_id'] = c1['id']
    resp = await cli.apply_json(config)
    snis = resp['snis']

    for sni in snis:
        sni.pop('created_at')
    assert snis == config['snis']

    # GET

    snis = await cli.snis.get_list()
    assert len(snis) == 2
    snis = {
        sni.data['name']: sni.data['ssl_certificate_id']
        for sni in snis
    }
    expected = {
        sni['name']: sni['ssl_certificate_id']
        for sni in config['snis']
    }
    assert snis == expected


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


async def test_pagination(cli):
    with open(os.path.join(PATH, 'test9.yaml')) as fp:
        await cli.apply_json(yaml.load(fp))
    consumers = []
    async for consumer in cli.consumers.paginate():
        consumers.append(consumer)
    assert len(consumers) >= 2


async def test_paginate_params(cli, consumer):
    await consumer.create_acls('test1')
    await consumer.create_acls('test2')
    consumer2 = await cli.consumers.create(username='an-xxxx-test')
    consumer3 = await cli.consumers.create(username='test-yy')
    await consumer2.create_acls('test2')
    await consumer3.create_acls('test3')
    users = [u async for u in cli.acls.paginate(group='test1', size=1)]
    assert len(users) == 1
    users = [u async for u in cli.acls.paginate(group='test2', size=1)]
    assert len(users) == 2
    acls = await consumer.acls(group='test2')
    assert len(acls) == 1
