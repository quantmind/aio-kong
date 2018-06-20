from .components import CrudComponent, ServiceEntity, KongError, KongEntity


class PluginMixin:

    def wrap(self, data):
        return Plugin(self.cli, data)

    @property
    def url(self) -> str:
        return '%s/%s' % (self.cli.url, self.name)

    def get_list(self, **params):
        url = '%s/%s' % (self.root.url, self.name)
        return self.execute(url, params=params, wrap=self.wrap_list)

    async def apply_json(self, data):
        if not isinstance(data, list):
            data = [data]
        plugins = await self.get_list()
        plugins = dict(((p['name'], p) for p in plugins))
        result = []
        for entry in data:
            name = entry.pop('name', None)
            if not name:
                raise KongError('Plugin name not specified')
            if name in plugins:
                plugin = plugins.pop(name)
                plugin = await self.update(
                    plugin.id, name=name, **entry)
            else:
                plugin = await self.create(name=name, **entry)

            result.append(plugin.data)
        for entry in plugins.values():
            await self.delete(entry['id'])
        return result

    async def preprocess_parameters(self, params):
        await anonymous(self.cli, params)
        preprocessor = PLUGIN_PREPROCESSORS.get(params.get('name'))
        if preprocessor:
            params = await preprocessor(self.cli, params)
        return params

    async def update(self, id, **params):
        params = await self.preprocess_parameters(params)
        return await super().update(id, **params)


class Plugins(PluginMixin, CrudComponent):
    pass


class ServicePlugins(PluginMixin, ServiceEntity):

    async def create(self, skip_error=None, **params):
        params['service_id'] = self.root.id
        params = await self.preprocess_parameters(params)
        return await self.execute(
            self.url, 'post', json=params,
            wrap=self.wrap, skip_error=skip_error
        )


class RoutePlugins(PluginMixin, CrudComponent):
    """Plugins associated with a Route
    """
    async def create(self, skip_error=None, **params):
        params['route_id'] = self.root.id
        params = await self.preprocess_parameters(params)
        return await self.execute(
            self.url, 'post', json=params,
            wrap=self.wrap, skip_error=skip_error
        )


class Plugin(KongEntity):
    pass


async def consumer_id_from_username(cli, params):
    if 'consumer_id' in params:
        c = await cli.consumers.get(params['consumer_id'])
        params['consumer_id'] = c['id']
    return params


async def anonymous(cli, params):
    if 'config' in params and 'anonymous' in params['config']:
        c = await cli.consumers.get(params['config']['anonymous'])
        params['config']['anonymous'] = c['id']
    return params


PLUGIN_PREPROCESSORS = {
    'request-termination': consumer_id_from_username
}
