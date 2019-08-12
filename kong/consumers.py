from .auths import auth_factory
from .components import CrudComponent, KongError
from .plugins import KongEntityWithPlugins


class Consumers(CrudComponent):
    def wrap(self, data):
        return Consumer(self, data)

    async def apply_credentials(self, auths, consumer):
        for auth_data in auths:
            auth = auth_factory(consumer, auth_data["type"])
            await auth.create_or_update_credentials(auth_data["config"])

    async def apply_json(self, data):
        if not isinstance(data, list):
            data = [data]
        result = []
        for entry in data:
            if not isinstance(entry, dict):
                raise KongError("dictionary required")
            groups = entry.pop("groups", [])
            auths = entry.pop("auths", [])
            udata = entry.copy()
            id_ = udata.pop("id", None)
            username = None
            if not id_:
                username = udata.pop("username", None)
                if not username:
                    raise KongError("Consumer username or id is required")
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
            current_groups = dict(((a["group"], a) for a in acls))
            for group in groups:
                if group not in current_groups:
                    await consumer.acls.create(group=group)
                else:
                    current_groups.pop(group)

            for acl in current_groups.values():
                await consumer.acls.delete(acl["id"])

            await self.apply_credentials(auths, consumer)

            result.append(consumer.data)

        return result


class Consumer(KongEntityWithPlugins):
    @property
    def username(self):
        return self.data.get("username")

    @property
    def acls(self):
        return CrudComponent(self, "acls")

    @property
    def jwts(self):
        return auth_factory(self, "jwt")

    @property
    def keyauths(self):
        return auth_factory(self, "key-auth")

    @property
    def basicauths(self):
        return auth_factory(self, "basic-auth")
