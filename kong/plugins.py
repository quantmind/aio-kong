from .components import CrudComponent, ServiceEntity, KongError, KongEntity


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

    def wrap(self, data):
        return Plugin.factory(self.cli, data)

    async def get_for_service(self, plugin_name, service_id):
        plugins = await self.get_list(name=plugin_name, service_id=service_id)
        if not plugins:
            raise KongError('Plugin %s not found' % plugin_name)
        return plugins[0]


class ServicePlugins(PluginJsonApply, ServiceEntity):

    def wrap(self, data):
        return Plugin.factory(self.cli, data)

    def create(self, skip_error=None, **params):
        params['service_id'] = self.root.id
        return self.execute(self.url, 'post', json=params,
                            wrap=self.wrap, skip_error=skip_error)


class Plugin(KongEntity):

    @classmethod
    def factory(cls, root, data):
        if data['name'] == 'jwt':
            return JWTPlugin(root, data)
        return Plugin(root, data)


class JWTPlugin(Plugin):

    def create_consumer_jwt(self, consumer, **params):
        return self.execute(
            '%s/jwt' % consumer.url, method='POST', json=params
        )

    def get_consumer_by_jwt(self, jwt):
        return self.execute(
            '%s/jwts/%s/consumer' % (self.root.url, jwt), method='GET',
            wrap=self.root.consumers.wrap
        )

    def remove_consumer_jwt(self, consumer, jwt):
        if isinstance(consumer, dict):
            consumer = self.root.consumers.wrap(consumer)
        return self.execute('%s/jwt/%s' % (consumer.url, jwt), method='DELETE')
