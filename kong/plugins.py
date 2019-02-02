from .components import CrudComponent, KongError, KongEntity


class Plugins(CrudComponent):

    async def create(self, **params):
        params = await self.preprocess_parameters(params)
        return await super().create(**params)

    async def apply_json(self, data):
        if not isinstance(data, list):
            data = [data]
        plugins = await self.get_full_list()
        if not self.is_entity:
            plugins = [p for p in plugins if self.root_plugin(p)]
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

    def root_plugin(self, plugin):
        return not (
            plugin.get('service') or
            plugin.get('route') or
            plugin.get('consumer')
        )

    async def preprocess_parameters(self, params):
        await anonymous(self.cli, params)
        preprocessor = PLUGIN_PREPROCESSORS.get(params.get('name'))
        if preprocessor:
            params = await preprocessor(self.cli, params)
        return params

    async def update(self, id, **params):
        params = await self.preprocess_parameters(params)
        return await super().update(id, **params)


class KongEntityWithPlugins(KongEntity):

    @property
    def plugins(self):
        return Plugins(self)


async def consumer_id_from_username(cli, params):
    if 'consumer.id' in params:
        c = await cli.consumers.get(params['consumer.id'])
        params['consumer.id'] = c['id']
    return params


async def anonymous(cli, params):
    if 'config' in params and 'anonymous' in params['config']:
        c = await cli.consumers.get(params['config']['anonymous'])
        params['config']['anonymous'] = c['id']
    return params


PLUGIN_PREPROCESSORS = {
    'request-termination': consumer_id_from_username
}
