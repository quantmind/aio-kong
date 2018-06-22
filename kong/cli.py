
import json
import asyncio

import click

import yaml as _yaml

from . import __version__
from .client import Kong, KongError


@click.command()
@click.option(
    '--version',
    is_flag=True,
    default=False,
    help='Display version and exit'
)
@click.option(
    '--yaml', type=click.File('r'),
    help='Yaml configuration to upload'
)
@click.pass_context
def kong(ctx, version, yaml):
    if version:
        click.echo(__version__)
        ctx.exit()
    return asyncio.get_event_loop().run_until_complete(_run(ctx, yaml))


async def _run(ctx, yaml):
    async with Kong() as cli:
        if yaml:
            try:
                result = await cli.apply_json(_yaml.load(yaml))
                click.echo(json.dumps(result, indent=4))
            except KongError as exc:
                raise click.ClickException(str(exc))
        else:
            click.echo(ctx.get_help())


def main():     # pragma    nocover
    kong()
