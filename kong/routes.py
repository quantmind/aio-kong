from itertools import zip_longest

from .components import CrudComponent
from .utils import as_list
from .plugins import KongEntityWithPlugins


class Routes(CrudComponent):
    """Kong Routes

    Routes are always associated with a Service
    """
    Entity = KongEntityWithPlugins

    async def delete(self, id_):
        route = self.wrap({'id': id_})
        await route.plugins.delete_all()
        return await super().delete(id_)

    async def apply_json(self, data):
        if not isinstance(data, list):
            data = [data]
        routes = await self.get_list()
        result = []
        for d, route in zip_longest(data, routes):
            if not d:
                if route:
                    await self.delete(route.id)
                continue
            plugins = d.pop('plugins', [])
            as_list('hosts', d)
            as_list('paths', d)
            as_list('methods', d)
            if not route:
                route = await self.create(**d)
            else:
                route = await self.update(route.id, **d)
            route.data['plugins'] = await route.plugins.apply_json(plugins)
            result.append(route.data)
        return result
