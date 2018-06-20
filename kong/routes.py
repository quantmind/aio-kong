from itertools import zip_longest

from .components import ServiceEntity, KongEntity
from .utils import as_list
from .plugins import RoutePlugins


class ServiceRoutes(ServiceEntity):
    """Routes associates with a service
    """
    def wrap(self, data):
        return Route(self, data)

    def create(self, skip_error=None, **params):
        params['service'] = dict(id=self.root.id)
        return self.execute(self.url, 'post', json=params,
                            wrap=self.wrap, skip_error=skip_error)

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


class Route(KongEntity):
    """Object representing a route
    """
    @property
    def plugins(self):
        return RoutePlugins(self, 'plugins')
