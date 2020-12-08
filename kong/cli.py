import asyncio
import click
import json
import yaml as _yaml

from . import __version__
from .client import Kong, KongError
from .utils import local_ip


@click.command()
@click.option("--version", is_flag=True, default=False, help="Display version and exit")
@click.option("--ip", is_flag=True, default=False, help="Show local IP address")
@click.option(
    "--key-auth", help="Create or display an authentication key for a consumer"
)
@click.option("--yaml", type=click.File("r"), help="Yaml configuration to upload")
@click.option(
    "--clear", default=False, is_flag=True, help="Clear objects not in configuration"
)
@click.pass_context
def kong(ctx, version, ip, key_auth, yaml, clear: bool):
    if version:
        click.echo(__version__)
    elif ip:
        click.echo(local_ip())
    elif key_auth:
        return _run(_auth_key(ctx, key_auth))
    elif yaml:
        return _run(_yml(ctx, yaml, clear))
    else:
        click.echo(ctx.get_help())


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


async def _yml(ctx, yaml, clear):
    async with Kong() as cli:
        try:
            result = await cli.apply_json(_yaml.safe_load(yaml), clear=clear)
            click.echo(json.dumps(result, indent=4))
        except KongError as exc:
            raise click.ClickException(str(exc))


async def _auth_key(ctx, consumer):
    async with Kong() as cli:
        try:
            c = await cli.consumers.get(consumer)
            keys = await c.keyauths.get_list()
            if keys:
                key = keys[0]
            else:
                key = await c.keyauths.create()
            click.echo(json.dumps(key.data, indent=4))
        except KongError as exc:
            raise click.ClickException(str(exc))


def main():  # pragma    nocover
    kong()
