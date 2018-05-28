from click.testing import CliRunner

from kong.cli import kong


def test_empty():
    runner = CliRunner()
    result = runner.invoke(kong, [])
    assert result.exit_code == 0
    assert result.output.startswith('Usage: kong [OPTIONS]')


def test_plugins():
    runner = CliRunner()
    result = runner.invoke(kong, ['--yaml', 'tests/test4.yaml'])
    assert result.exit_code == 0


def test_bad_config():
    runner = CliRunner()
    result = runner.invoke(kong, ['--yaml', 'tests/test5.yaml'])
    assert result.exit_code == 1
    assert result.output.strip() == 'Error: Plugin name not specified'
