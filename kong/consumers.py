from .components import CrudComponent, KongError
from .plugins import KongEntityWithPlugins


class Consumers(CrudComponent):

    def wrap(self, data):
        return Consumer(self, data)

    async def apply_json(self, data):
        if not isinstance(data, list):
            data = [data]
        result = []
        for entry in data:
            if not isinstance(entry, dict):
                raise KongError('dictionary required')
            groups = entry.pop('groups', [])
            udata = entry.copy()
            id_ = udata.pop('id', None)
            username = None
            if not id_:
                username = udata.pop('username', None)
                if not username:
                    raise KongError('Consumer username or id is required')
            uid = id_ or username
            try:
                consumer = await self.get(uid)
            except KongError as exc:
                if exc.status == 404:
                    consumer = await self.create(**entry)
                else:
                    raise
            else:
                if entry:
                    consumer = await self.update(uid, **udata)
            acls = await consumer.acls.get_list()
            current_groups = dict(((a['group'], a) for a in acls))
            for group in groups:
                if group not in current_groups:
                    await consumer.acls.create(group=group)
                else:
                    current_groups.pop(group)

            for acl in current_groups.values():
                await consumer.acls.delete(acl['id'])

            result.append(consumer.data)

        return result


class ConsumerAuth(CrudComponent):

    @property
    def url(self) -> str:
        return f'{self.root.url}/{self.name}'

    async def create(self):
        return await self.cli.execute(
            self.url, 'POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            wrap=self.wrap
        )

    async def get_or_create(self):
        secrets = await self.get_list(limit=1)
        return secrets[0] if secrets else await self.create()


class Consumer(KongEntityWithPlugins):

    @property
    def username(self):
        return self.data.get('username')

    @property
    def acls(self):
        return CrudComponent(self, 'acls')

    @property
    def jwts(self):
        return ConsumerAuth(self, 'jwt')

    @property
    def keyauths(self):
        return ConsumerAuth(self, 'key-auth')
