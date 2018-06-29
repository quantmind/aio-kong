from .components import CrudComponent, KongEntity, KongError
from .routes import ServiceRoutes
from .plugins import ServicePlugins
from .utils import local_ip


REMOVE = frozenset(('absent', 'remove'))
LOCAL_HOST = frozenset(('localhost', '127.0.0.1'))


class Services(CrudComponent):
    """Kong API component"""
    def wrap(self, data):
        return Service(self, data)

    async def remove(self, id):
        s = await self.get(id)
        await s.routes.delete_all()
        await self.delete(id)

    async def apply_json(self, data):
        """Apply a JSON data object for a service
        """
        if not isinstance(data, list):
            data = [data]
        result = []
        for entry in data:
            if not isinstance(entry, dict):
                raise KongError('dictionary required')
            ensure = entry.pop('ensure', None)
            name = entry.pop('name', None)
            routes = entry.pop('routes', [])
            plugins = entry.pop('plugins', [])
            host = entry.pop('host', None)
            if host in LOCAL_HOST:
                host = local_ip()
            if not name:
                raise KongError('Service name is required')
            if ensure in REMOVE:
                if await self.has(name):
                    await self.remove(name)
                continue
            # backward compatible with config entry
            config = entry.pop('config', None)
            if isinstance(config, dict):
                entry.update(config)
            if await self.has(name):
                srv = await self.update(name, host=host, **entry)
            else:
                srv = await self.create(name=name, host=host, **entry)
            srv.data['routes'] = await srv.routes.apply_json(routes)
            srv.data['plugins'] = await srv.plugins.apply_json(plugins)
            result.append(srv.data)
        return result


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
