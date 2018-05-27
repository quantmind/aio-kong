from click.testing import CliRunner

from kong.cli import start


def test_git():
    runner = CliRunner()
    result = runner.invoke(start, ['--yaml', 'tests/test4.yaml'])
    assert result.exit_code == 0
