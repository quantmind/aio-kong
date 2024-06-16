import os

import pytest
import yaml

from kong.client import Kong, KongError

PATH = os.path.dirname(__file__)


async def apply(cli, file_name):
    with open(os.path.join(PATH, file_name)) as fp:
        manifest = yaml.load(fp, Loader=yaml.FullLoader)
    await cli.apply_json(manifest)


async def test_json(cli):
    await apply(cli, "test.yaml")
    srv = await cli.services.get("foo")
    routes = await srv.routes.get_list()
    assert len(routes) == 2
    #
    # check plugins
    plugins = await srv.plugins.get_list()
    assert len(plugins) == 2


async def test_json2(cli):
    await apply(cli, "test2.yaml")
    srv = await cli.services.get("foo")
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
        await apply(cli, "test3.yaml")

    assert str(cli) == cli.url


async def test_json_plugins(cli):
    await apply(cli, "test4.yaml")


async def test_json_route_plugins(cli: Kong):
    await apply(cli, "test6.yaml")
    await apply(cli, "test6.yaml")
    srv = await cli.services.get("pippo")
    plugins = await srv.plugins.get_list()
    assert len(plugins) == 1
    routes = await srv.routes.get_list()
    assert len(routes) == 1
    plugins = await routes[0].plugins.get_list()
    assert len(plugins) == 3
    cs = await cli.consumers.get("an-xxxx-test")
    acls = await cs.acls.get_list()
    assert len(acls) == 2
    plugin_map = {p.name: p for p in plugins}
    termination = plugin_map["request-termination"]
    assert termination["consumer"]

    await apply(cli, "test61.yaml")
    srv = await cli.services.get("pippo")
    plugins = await srv.plugins.get_list()
    assert len(plugins) == 0
    routes = await srv.routes.get_list()
    assert len(routes) == 1
    plugins = await routes[0].plugins.get_list()
    assert len(plugins) == 1
    cs = await cli.consumers.get("an-xxxx-test")
    acls = await cs.acls.get_list()
    assert len(acls) == 1


async def test_auth_handling(cli):
    await apply(cli, "test_auth.yaml")
    consumer = await cli.consumers.get("admin")

    basic_auths = await consumer.basicauths.get_list()
    assert len(basic_auths) == 1
    assert basic_auths[0]["username"] == "admin_creds"

    key_auths = await consumer.keyauths.get_list()
    assert len(key_auths) == 1


async def test_auth_overwrite(cli):
    await apply(cli, "test_auth.yaml")
    await apply(cli, "test_auth_overwrite.yaml")
    consumer = await cli.consumers.get("admin")

    basic_auths = await consumer.basicauths.get_list()
    assert len(basic_auths) == 1
    assert basic_auths[0]["username"] == "admin_creds"

    key_auths = await consumer.keyauths.get_list()
    assert len(key_auths) == 1


async def test_ensure_remove(cli):
    await apply(cli, "test6.yaml")
    assert await cli.services.has("pippo") is True
    await apply(cli, "test7.yaml")
    assert await cli.services.has("pippo") is False
    await apply(cli, "test7.yaml")
    assert await cli.services.has("pippo") is False
