from typing import cast

from .components import UUID, CrudComponent, JsonType
from .plugins import KongEntityWithPlugins
from .utils import as_list


class Route(KongEntityWithPlugins):
    pass


class Routes(CrudComponent):
    """Kong Routes

    Routes are always associated with a Service
    """

    async def delete(self, id_: str | UUID) -> bool:
        route = cast(KongEntityWithPlugins, self.wrap({"id": id_}))
        await route.plugins.delete_all()
        return await super().delete(id_)

    async def apply_json(self, data: JsonType, clear: bool = True) -> list[dict]:
        if not isinstance(data, list):
            data = [data]
        routes = await self.get_list()
        route_map = {r.name: r for r in routes}
        result = []
        for entry in data:
            name = entry.get("name")
            route = route_map.pop(name, None) if name else None
            entry = entry.copy()
            plugins = entry.pop("plugins", [])
            as_list("hosts", entry)
            as_list("paths", entry)
            as_list("methods", entry)
            if route:
                await self.delete(route.id)
            entity = await self.create(**entry)
            route = cast(KongEntityWithPlugins, entity)
            route.data["plugins"] = await route.plugins.apply_json(plugins)
            result.append(route.data)
        if clear:
            for route in route_map.values():
                await self.delete(route.id)
        return result
