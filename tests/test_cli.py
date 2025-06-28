import json

from click.testing import CliRunner

from kong import __version__
from kong.cli import kong
from kong.utils import local_ip


def test_empty():
    runner = CliRunner()
    result = runner.invoke(kong, ["--help"])
    assert result.exit_code == 0
    assert result.output.startswith("Usage: kong [OPTIONS]")


def test_version():
    runner = CliRunner()
    result = runner.invoke(kong, ["--version"])
    assert result.exit_code == 0
    assert result.output.rstrip().split()[-1] == __version__


def test_ip():
    runner = CliRunner()
    result = runner.invoke(kong, ["ip"])
    assert result.exit_code == 0
    assert result.output.rstrip() == local_ip()


def test_plugins():
    runner = CliRunner()
    result = runner.invoke(kong, ["yaml", "tests/configs/test4.yaml"])
    assert result.exit_code == 0


def test_bad_config():
    runner = CliRunner()
    result = runner.invoke(kong, ["yaml", "tests/configs/test5.yaml"])
    assert result.exit_code == 1
    assert result.output.strip() == "Error: Plugin name not specified"


def test_key_auth():
    runner = CliRunner()
    result = runner.invoke(kong, ["key-auth", "foo"])
    assert result.exit_code == 1
    result = runner.invoke(kong, ["yaml", "tests/configs/test8.yaml"])
    assert result.exit_code == 0
    result = runner.invoke(kong, ["key-auth", "an-xxxx-test"])
    assert result.exit_code == 0
    data = json.loads(result.output.rstrip())
    result = runner.invoke(kong, ["key-auth", "an-xxxx-test"])
    assert result.exit_code == 0
    data2 = json.loads(result.output.rstrip())
    assert data["key"] == data2["key"]


def test_consumers():
    runner = CliRunner()
    result = runner.invoke(kong, ["consumers", "--json"])
    assert result.exit_code == 0
    result = runner.invoke(kong, ["consumers"])
    assert result.exit_code == 0


def test_services():
    runner = CliRunner()
    result = runner.invoke(kong, ["yaml", "tests/configs/test.yaml"])
    assert result.exit_code == 0
    result = runner.invoke(kong, ["services", "--json"])
    assert result.exit_code == 0
    result = runner.invoke(kong, ["services"])
    assert result.exit_code == 0


def test_routes():
    runner = CliRunner()
    result = runner.invoke(kong, ["routes", "foo", "--json"])
    assert result.exit_code == 0
    result = runner.invoke(kong, ["routes", "foo"])
    assert result.exit_code == 0


def test_no_routes():
    runner = CliRunner()
    result = runner.invoke(kong, ["routes", "foox"])
    assert result.exit_code == 1


def test_delete_service():
    runner = CliRunner()
    result = runner.invoke(kong, ["services", "-d", "foo"])
    assert result.exit_code == 0
    result = runner.invoke(kong, ["services", "-d", "foo"])
    assert result.exit_code == 1
