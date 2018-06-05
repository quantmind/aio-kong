import pytest
from kong.plugins import JWTPlugin
from kong.client import KongError


@pytest.fixture(scope='function')
async def clear_consumers(cli):
    consumers = await cli.consumers.get_list()
    for consumer in consumers:
        await cli.consumers.delete(consumer.id)


@pytest.fixture(scope='session')
async def jwt_plugin(cli):
    service = await cli.services.get('test')
    jwt = await service.plugins.create(name='jwt')
    return jwt


async def test_create_jwt_plugin(jwt_plugin):
    assert isinstance(jwt_plugin, JWTPlugin)


async def test_jwt_create_token(cli, jwt_plugin, clear_consumers):
    consumer = await cli.consumers.create(custom_id='123456')
    token = await jwt_plugin.create_consumer_token(consumer)
    assert token is not None


async def test_jwt_consumer_by_token(cli, jwt_plugin, clear_consumers):
    consumer = await cli.consumers.create(custom_id='123456')
    token = await jwt_plugin.create_consumer_token(consumer)
    jwt_consumer = await jwt_plugin.get_consumer_by_token(token)
    assert consumer.id == jwt_consumer.id


async def test_jwt_remove_token(cli, jwt_plugin, clear_consumers):
    consumer = await cli.consumers.create(custom_id='123456')
    token = await jwt_plugin.create_consumer_token(consumer)
    await jwt_plugin.remove_consumer_token(consumer, token)
    with pytest.raises(KongError):
        await jwt_plugin.get_consumer_by_token(token)
