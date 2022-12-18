from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .components import UUID, CrudComponent, JsonType, KongEntity, KongError

if TYPE_CHECKING:
    from .client import Kong


class Plugins(CrudComponent):
    async def create(self, **params: Any) -> KongEntity:
        params = await self.preprocess_parameters(params)
        return await super().create(**params)

    async def apply_json(self, data: JsonType, clear: bool = True) -> list:
        if not isinstance(data, list):
            data = [data]
        plugins = await self.get_full_list()
        if not self.is_entity:
            plugins = [p for p in plugins if self.root_plugin(p)]
        plugin_map = {p["name"]: p for p in plugins}
        result = []
        for entry in data:
            entry = entry.copy()
            name = entry.pop("name", None)
            if not name:
                raise KongError("Plugin name not specified")
            if name in plugin_map:
                plugin = plugin_map.pop(name)
                plugin = await self.update(plugin.id, name=name, **entry)
            else:
                plugin = await self.create(name=name, **entry)

            result.append(plugin.data)
        # left over plugins
        if clear:
            for entry in plugin_map.values():
                await self.delete(entry["id"])
        return result

    def root_plugin(self, plugin: KongEntity) -> bool:
        return not (
            plugin.get("service") or plugin.get("route") or plugin.get("consumer")
        )

    async def preprocess_parameters(self, params: dict) -> dict:
        await anonymous(self.cli, params)
        if preprocessor := PLUGIN_PREPROCESSORS.get(params.get("name", "")):
            params = await preprocessor(self.cli, params)
        return params

    async def update(self, id_: str | UUID, **params: Any) -> KongEntity:
        params = await self.preprocess_parameters(params)
        return await super().update(id_, **params)


class KongEntityWithPlugins(KongEntity):
    @property
    def plugins(self) -> Plugins:
        return Plugins(self)


async def consumer_id_from_username(cli: Kong, params: dict) -> dict:
    if "id" in (params.get("consumer") or {}):
        c = await cli.consumers.get(params["consumer"]["id"])
        params["consumer"]["id"] = c["id"]
    return params


async def anonymous(cli: Kong, params: dict) -> dict:
    if "config" in params and "anonymous" in params["config"]:
        c = await cli.consumers.get(params["config"]["anonymous"])
        params["config"]["anonymous"] = c["id"]
    return params


PLUGIN_PREPROCESSORS = {"request-termination": consumer_id_from_username}
