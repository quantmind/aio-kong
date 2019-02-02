import pytest

from kong.client import KongResponseError


async def test_consumer(cli, consumer):
    assert consumer.username == 'test-xx'
    assert consumer.get('custom_id') is None


async def test_jwt_create(cli, consumer):
    jwt = await consumer.jwts.create()
    assert jwt['consumer']['id'] == consumer.id
    data = await consumer.jwts.get_list()
    assert data
    data = [d for d in data if d['id'] == jwt['id']]
    assert data
    jwt2 = await consumer.jwts.get(jwt['id'])
    assert jwt.data == jwt2.data


async def test_jwt_delete(cli, consumer):
    jwt = await consumer.jwts.create()
    assert jwt['consumer']['id'] == consumer.id
    await consumer.jwts.delete(jwt['id'])
    with pytest.raises(KongResponseError) as e:
        await consumer.jwts.delete(jwt['id'])
    assert e.value.response.status == 404


async def test_get_or_create_jwt(cli, consumer):
    jwt1 = await consumer.jwts.get_or_create()
    jwt2 = await consumer.jwts.get_or_create()
    assert jwt1.data == jwt2.data


async def test_key_auth_create(cli, consumer):
    auth = await consumer.keyauths.create()
    assert auth['consumer']['id'] == consumer.id


async def test_key_auth_delete(cli, consumer):
    auth = await consumer.keyauths.create()
    assert auth['consumer']['id'] == consumer.id
    await consumer.keyauths.delete(auth['id'])
    with pytest.raises(KongResponseError) as e:
        await consumer.keyauths.delete(auth['id'])
    assert e.value.response.status == 404


async def test_group(cli, consumer):
    r = await consumer.acls.create(group='a')
    assert r['consumer']['id'] == consumer.id
    assert r['group'] == 'a'
    r = await consumer.acls.create(group='b')
    assert r['consumer']['id'] == consumer.id
    assert r['group'] == 'b'
