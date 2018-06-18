from .components import CrudComponent, KongEntity, KongError


class Consumers(CrudComponent):

    def wrap(self, data):
        return Consumer(self, data)

    async def apply_json(self, data):
        if not isinstance(data, list):
            data = [data]
        consumers = await self.get_list()
        consumers = dict(((c.username, c) for c in consumers if c.username))
        result = []
        for entry in data:
            if not isinstance(entry, dict):
                raise KongError('dictionary required')
            username = entry.pop('username', None)
            if not username:
                raise KongError('Consumer username is required')
            if username in consumers:
                if entry:
                    consumer = await self.update(username, **entry)
                else:
                    consumer = consumers[username]
                consumers.pop(username)
            else:
                consumer = await self.create(username=username, **entry)

            result.append(consumer.data)

        return result


class Consumer(KongEntity):

    @property
    def username(self):
        return self.data.get('username')
