import os


PATH = os.path.join(os.path.dirname(__file__), 'certificates')


def read(name):
    with open(os.path.join(PATH, name)) as fp:
        return fp.read()


def test_client(cli):
    assert cli.session


async def test_create_service(cli):
    srv = await cli.services.create(
        name='test', host='example.upstream', port=8080
    )
    assert srv.name == 'test'
    assert srv.host == 'example.upstream'
    assert srv.id
    assert srv.routes.root == srv
    assert srv.plugins.root == srv


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


async def test_add_certificate(cli):
    c = await cli.certificates.create(
        cert=read('cert1.pem'),
        key=read('key1.pem')
    )
    assert c.id
    assert len(c.data['snis']) == 0
    snis = await c.snis.get_list()
    assert snis == []
    await cli.certificates.delete(c.id)


async def test_snis(cli):
    c1 = await cli.certificates.create(
        cert=read('cert1.pem'),
        key=read('key1.pem')
    )
    c2 = await cli.certificates.create(
        cert=read('cert2.pem'),
        key=read('key2.pem')
    )
    config = {
        'snis': [
            {
                'name': 'a1.example.com',
                'certificate': {
                    'id': c1['id']
                }
            },
            {
                'name': 'a2.example.com',
                'certificate': {
                    'id': c2['id']
                }
            },
        ]
    }
    resp = await cli.apply_json(config)
    snis = resp['snis']

    # CREATE
    for sni in snis:
        sni.pop('created_at')
        sni.pop('id')
    assert snis == config['snis']

    # UPDATE
    config['snis'][0]['certificate'] = {'id': c2['id']}
    config['snis'][1]['certificate'] = {'id': c1['id']}
    resp = await cli.apply_json(config)
    snis = resp['snis']

    for sni in snis:
        sni.pop('created_at')
        sni.pop('id')
    assert snis == config['snis']

    # GET

    snis = await cli.snis.get_list()
    assert len(snis) == 2
    snis = {
        sni.data['name']: sni.data['certificate']['id']
        for sni in snis
    }
    expected = {
        sni['name']: sni['certificate']['id']
        for sni in config['snis']
    }
    assert snis == expected


async def test_paginate_params(cli, consumer):
    await consumer.acls.create(group='test1')
    await consumer.acls.create(group='test2')
    consumer2 = await cli.consumers.create(username='an-xxxx-test')
    consumer3 = await cli.consumers.create(username='test-yy')
    await consumer2.acls.create(group='test2')
    await consumer3.acls.create(group='test3')
    acls = [u async for u in cli.acls.paginate(size=1)]
    assert len(acls) == 4
    acls = [u async for u in consumer.acls.paginate(size=1)]
    assert len(acls) == 2
