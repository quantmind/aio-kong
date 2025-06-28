import asyncio
import json
from typing import Any, cast

import click
import yaml as _yaml
from rich.console import Console
from rich.table import Table

from . import __version__
from .client import Kong, KongError, default_admin_url
from .components import KongEntity
from .consumers import Consumer
from .utils import local_ip

admin_url = click.option(
    "--url", default=default_admin_url(), help="Kong Admin URL", show_default=True
)

as_json = click.option("--json", default=False, is_flag=True, help="Output as JSON")


@click.group()
@click.version_option(version=__version__)
def kong() -> None:
    """Kong CLI - Manage Kong Gateway configurations."""
    pass


@kong.command()
@click.argument(
    "yaml",
    type=click.File("r"),
)
@click.option(
    "--clear",
    default=False,
    is_flag=True,
    help="Clear objects not in configuration",
)
@admin_url
def yaml(
    yaml: click.File,
    clear: bool,
    url: str,
) -> None:
    "Upload a configuration from a yaml file"
    asyncio.run(_yml(yaml, clear, url))


@kong.command()
def ip() -> None:
    "Show local IP address"
    click.echo(local_ip())


@kong.command()
@click.option("-d", "--delete", type=str, help="Delete a service by name")
@admin_url
@as_json
def services(delete: str, url: str, json: bool) -> None:
    "Display services"
    asyncio.run(_services(url, as_json=json, delete=delete))


@kong.command()
@click.argument("service")
@admin_url
@as_json
def routes(service: str, url: str, json: bool) -> None:
    "Display routes for a service"
    asyncio.run(_routes(service, url, as_json=json))


@kong.command()
@admin_url
@as_json
def consumers(url: str, json: bool) -> None:
    "Display consumers"
    asyncio.run(_consumers(url, as_json=json))


@kong.command()
@click.argument("consumer")
@admin_url
def key_auth(consumer: str, url: str) -> None:
    "Create or display an authentication key for a consumer"
    asyncio.run(_auth_key(consumer, url))


async def _yml(yaml: Any, clear: bool, url: str) -> None:
    async with Kong(url=url) as cli:
        try:
            result = await cli.apply_json(_yaml.safe_load(yaml), clear=clear)
            display_json(result)
        except KongError as exc:
            raise click.ClickException(str(exc)) from None


async def _services(url: str, as_json: bool = False, delete: str | None = None) -> None:
    async with Kong(url=url) as cli:
        try:
            if delete:
                await cli.services.delete(delete)
                click.echo(f"Service '{delete}' deleted.")
                return
            services = await cli.services.get_full_list()
        except KongError as exc:
            raise click.ClickException(str(exc)) from None
        if as_json:
            display_json(services)
            return
        table = Table(title="Services")
        columns = ["Name", "Host", "Port", "Protocol", "Path", "Tags", "ID"]
        for column in columns:
            table.add_column(column)
        for s in sorted(services, key=lambda s: s.name):
            table.add_row(*[str_value(s.data, column) for column in columns])
        console = Console()
        console.print(table)


async def _routes(service: str, url: str, as_json: bool = False) -> None:
    async with Kong(url=url) as cli:
        try:
            svc = await cli.services.get(service)
            routes = await svc.routes.get_full_list()
        except KongError as exc:
            raise click.ClickException(str(exc)) from None
        if as_json:
            display_json(routes)
            return
        table = Table(title="Services")
        columns = [
            "Name",
            "Hosts",
            "Protocols",
            "Path",
            "Tags",
            "Strip Path",
            "Preserve Host",
            "ID",
        ]
        for column in columns:
            table.add_column(column)
        for s in sorted(routes, key=lambda s: s.name):
            table.add_row(*[str_value(s.data, column) for column in columns])
        console = Console()
        console.print(table)


async def _consumers(url: str, as_json: bool = False) -> None:
    async with Kong(url=url) as cli:
        try:
            consumers = await cli.consumers.get_full_list()
        except KongError as exc:
            raise click.ClickException(str(exc)) from None
        if as_json:
            display_json(consumers)
            return
        table = Table(title="Consumers")
        columns = ["Username", "ID", "Custom ID", "Tags"]
        for column in columns:
            table.add_column(column)
        for c in sorted(consumers, key=lambda s: s.name):
            table.add_row(*[str_value(c.data, column) for column in columns])
        console = Console()
        console.print(table)


async def _auth_key(consumer: str, admin_url: str) -> None:
    async with Kong(url=admin_url) as cli:
        try:
            c = cast(Consumer, await cli.consumers.get(consumer))
            keys = await c.keyauths.get_list()
            if keys:
                key = keys[0]
            else:
                key = await c.keyauths.create()
            display_json(key)
        except KongError as exc:
            raise click.ClickException(str(exc)) from None


def str_value(data: dict, key: str) -> str:
    key = key.lower().replace(" ", "_")
    value = data.get(key)
    if value is None:
        return ""
    elif isinstance(value, bool):
        return ":white_check_mark:" if value else "[red]:x:"
    elif isinstance(value, list):
        return ", ".join(str(v) for v in value)
    else:
        return str(value)


def display_json(data: Any) -> None:
    """Display data as JSON."""
    click.echo(json.dumps(data, indent=2, default=kong_entity))


def kong_entity(obj: Any) -> Any:
    if isinstance(obj, KongEntity):
        return obj.data
    raise TypeError(
        f"Cannot serialize {type(obj).__name__} to JSON"
    )  # pragma: no cover
