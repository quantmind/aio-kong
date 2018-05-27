from .components import CrudComponent, ServiceEntity, KongError


class PluginJsonApply:

    async def apply_json(self, data):
        if not isinstance(data, list):
            data = [data]
        plugins = await self.get_list()
        plugins = dict(((p['name'], p) for p in plugins))
        result = []
        for entry in data:
            name = entry.get('name')
            if not name:
                raise KongError('Plugin name not specified')
            if name in plugins:
                plugin = plugins.pop(name)
                config = entry.get('config') or {}
                plugin = await self.update(plugin['id'], config=config)
            else:
                plugin = await self.create(**entry)

            result.append(plugin)
        for entry in plugins.values():
            await self.delete(entry['id'])
        return result


class Plugins(PluginJsonApply, CrudComponent):
    pass


class ServicePlugins(PluginJsonApply, ServiceEntity):

    def create(self, skip_error=None, **params):
        params['service_id'] = self.root.id
        return self.execute(self.url, 'post', json=params,
                            wrap=self.wrap, skip_error=skip_error)
