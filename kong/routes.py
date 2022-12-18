from itertools import zip_longest
from typing import cast

from .components import UUID, CrudComponent, JsonType
from .plugins import KongEntityWithPlugins
from .utils import as_list


class Routes(CrudComponent):
    """Kong Routes

    Routes are always associated with a Service
    """

    Entity = KongEntityWithPlugins

    async def delete(self, id_: str | UUID) -> bool:
        route = cast(KongEntityWithPlugins, self.wrap({"id": id_}))
        await route.plugins.delete_all()
        return await super().delete(id_)

    async def apply_json(self, data: JsonType, clear: bool = True) -> list:
        if not isinstance(data, list):
            data = [data]
        routes = await self.get_list()
        result = []
        for entry, route in zip_longest(data, routes):
            if not entry:
                if route and clear:
                    await self.delete(route.id)
                continue
            entry = entry.copy()
            plugins = entry.pop("plugins", [])
            as_list("hosts", entry)
            as_list("paths", entry)
            as_list("methods", entry)
            if not route:
                entity = await self.create(**entry)
            else:
                entity = await self.update(route.id, **entry)
            route = cast(KongEntityWithPlugins, entity)
            route.data["plugins"] = await route.plugins.apply_json(plugins)
            result.append(route.data)
        return result
