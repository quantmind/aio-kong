
import asyncio

import click

import yaml as _yaml

from kong.client import Kong, KongError


@click.command()
@click.option(
    '--yaml', type=click.File('r'),
    help='Yaml configuration to upload'
)
def start(yaml):
    return asyncio.get_event_loop().run_until_complete(_run(yaml))


async def _run(yaml):
    async with Kong() as cli:
        if yaml:
            try:
                result = await cli.apply_json(_yaml.load(yaml))
                click.echo(result)
            except KongError as exc:
                raise click.ClickError(str(exc))


def main():     # noqa
    start()
