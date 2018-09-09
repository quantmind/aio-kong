import pytest

from kong.client import KongError


async def test_consumer(cli, consumer):
    assert consumer.username == 'test-xx'
    assert consumer.get('custom_id', '') == ''


async def test_jwt_create(cli, consumer):
    jwt = await consumer.create_jwt()
    assert jwt['consumer_id'] == consumer.id
    data = await consumer.jwts()
    assert data
    data = [d for d in data if d['id'] == jwt['id']]
    assert data


@pytest.mark.parametrize('keyname', ('key', 'id'))
async def test_consumer_from_jwt(cli, consumer, keyname):
    jwt = await consumer.create_jwt()
    consumer_ = await cli.jwts.get_consumer(jwt[keyname])
    assert consumer_['id'] == jwt['consumer_id']


async def test_jwt_delete(cli, consumer):
    jwt = await consumer.create_jwt()
    assert jwt['consumer_id'] == consumer.id
    await consumer.delete_jwt(jwt['id'])
    with pytest.raises(KongError):
        await consumer.delete_jwt(jwt['id'])


async def test_key_auth_create(cli, consumer):
    auth = await consumer.create_key_auth()
    assert auth['consumer_id'] == consumer.id


async def test_key_auth_delete(cli, consumer):
    auth = await consumer.create_key_auth()
    assert auth['consumer_id'] == consumer.id
    await consumer.delete_key_auth(auth['id'])
    with pytest.raises(KongError):
        await consumer.delete_key_auth(auth['id'])


async def test_group(cli, consumer):
    r = await consumer.create_acls('a')
    assert r['consumer_id'] == consumer.id
    assert r['group'] == 'a'
    r = await consumer.create_acls('b')
    assert r['consumer_id'] == consumer.id
    assert r['group'] == 'b'
