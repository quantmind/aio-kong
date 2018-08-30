from .components import CrudComponent, KongEntity, KongError


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
            username = entry.pop('username', None)
            groups = entry.pop('groups', [])
            if not username:
                raise KongError('Consumer username is required')
            try:
                consumer = await self.get(username)
            except KongError as exc:
                if exc.status == 404:
                    consumer = await self.create(username=username, **entry)
                else:
                    raise
            else:
                if entry:
                    consumer = await self.update(username, **entry)
            acls = await consumer.acls()
            current_groups = dict(((a['group'], a) for a in acls))
            for group in groups:
                if group not in current_groups:
                    await consumer.create_acls(group)
                else:
                    current_groups.pop(group)

            for acl in current_groups.values():
                await consumer.delete_acls(acl['id'])

            result.append(consumer.data)

        return result


class Consumer(KongEntity):

    @property
    def username(self):
        return self.data.get('username')

    async def jwts(self):
        url = f'{self.url}/jwt'
        result = await self.cli.execute(url, 'GET')
        return result['data']

    def create_jwt(self):
        url = f'{self.url}/jwt'
        return self.cli.execute(
            url, 'POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

    def delete_jwt(self, id):
        url = f'{self.url}/jwt/{id}'
        return self.cli.execute(url, 'DELETE')

    async def key_auths(self):
        url = f'{self.url}/key-auth'
        result = await self.cli.execute(url, 'GET')
        return result['data']

    def create_key_auth(self):
        url = f'{self.url}/key-auth'
        return self.cli.execute(
            url, 'POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

    def delete_key_auth(self, id):
        url = f'{self.url}/key-auth/{id}'
        return self.cli.execute(url, 'DELETE')

    def create_acls(self, group):
        url = f'{self.url}/acls'
        return self.cli.execute(url, 'POST', json=dict(group=group))

    def delete_acls(self, id):
        url = f'{self.url}/acls/{id}'
        return self.cli.execute(url, 'DELETE')

    def acls(self, **params):
        params['consumer_id'] = self.id
        return self.cli.acls.get_list(**params)
