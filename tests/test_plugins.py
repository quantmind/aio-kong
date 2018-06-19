import pytest

from kong.client import KongError


@pytest.fixture()
async def consumer(cli, service):
    await service.plugins.create(name='jwt')
    consumer = await cli.consumers.create(username='test-xx')
    return consumer


async def test_jwt_create(cli, consumer):
    jwt = await consumer.create_jwt()
    assert jwt['consumer_id'] == consumer.id


async def test_jwt_delete(cli, consumer):
    jwt = await consumer.create_jwt()
    assert jwt['consumer_id'] == consumer.id
    await consumer.delete_jwt(jwt['id'])
    with pytest.raises(KongError):
        await consumer.delete_jwt(jwt['id'])
