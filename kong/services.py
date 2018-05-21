from .components import CrudComponent, KongEntity
from .routes import ServiceRoutes
from .plugins import ServicePlugins


class Services(CrudComponent):
    """Kong API component"""
    def wrap(self, data):
        return Service(self, data)

    async def remove(self, id):
        print('getting %s' % id)
        s = await self.get(id)
        print('removing %s routes' % id)
        await s.routes.delete_all()
        print('removing %s' % id)
        await self.delete(id)

    async def apply_json(self, data):
        """Apply a JSON data object for a service
        """
        name = data.get('name')
        if not name:
            raise ValueError('name is required')
        config = data.get('config')
        if not config:
            raise ValueError('config dictionary for %s is required' % name)

        if await self.has(name):
            srv = await self.update(name, **config)
        else:
            srv = await self.create(name=name, **config)

        srv.data['routes'] = await srv.routes.apply_json(
            data.get('routes') or []
        )

        plugins = data.get('plugins')

        if plugins:
            srv.data['plugins'] = await srv.plugins.apply_json(plugins)

        return srv


class Service(KongEntity):
    """Object representing a service
    """
    @property
    def plugins(self):
        return ServicePlugins(self, 'plugins')

    @property
    def routes(self):
        return ServiceRoutes(self, 'routes')

    @property
    def name(self):
        return self.data['name']

    @property
    def host(self):
        return self.data.get('host')
