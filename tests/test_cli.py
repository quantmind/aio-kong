import json

from click.testing import CliRunner

from kong import __version__
from kong.cli import kong
from kong.utils import local_ip


def test_empty():
    runner = CliRunner()
    result = runner.invoke(kong, [])
    assert result.exit_code == 0
    assert result.output.startswith('Usage: kong [OPTIONS]')


def test_version():
    runner = CliRunner()
    result = runner.invoke(kong, ['--version'])
    assert result.exit_code == 0
    assert result.output.rstrip() == __version__


def test_ip():
    runner = CliRunner()
    result = runner.invoke(kong, ['--ip'])
    assert result.exit_code == 0
    assert result.output.rstrip() == local_ip()


def test_plugins():
    runner = CliRunner()
    result = runner.invoke(kong, ['--yaml', 'tests/test4.yaml'])
    assert result.exit_code == 0


def test_bad_config():
    runner = CliRunner()
    result = runner.invoke(kong, ['--yaml', 'tests/test5.yaml'])
    assert result.exit_code == 1
    assert result.output.strip() == 'Error: Plugin name not specified'


def test_key_auth():
    runner = CliRunner()
    result = runner.invoke(kong, ['--key-auth', 'foo'])
    assert result.exit_code == 1
    result = runner.invoke(kong, ['--yaml', 'tests/test8.yaml'])
    assert result.exit_code == 0
    result = runner.invoke(kong, ['--key-auth', 'an-xxxx-test'])
    assert result.exit_code == 0
    data = json.loads(result.output.rstrip())
    result = runner.invoke(kong, ['--key-auth', 'an-xxxx-test'])
    assert result.exit_code == 0
    data2 = json.loads(result.output.rstrip())
    assert data['key'] == data2['key']
