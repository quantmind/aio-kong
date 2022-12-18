from typing import cast

from .auths import ConsumerAuth, auth_factory
from .components import CrudComponent, JsonType, KongError, KongResponseError
from .plugins import KongEntityWithPlugins


class Consumer(KongEntityWithPlugins):
    @property
    def username(self) -> str:
        return self.data.get("username", "")

    @property
    def acls(self) -> CrudComponent:
        return CrudComponent(self, "acls")

    @property
    def jwts(self) -> ConsumerAuth:
        return auth_factory(self, "jwt")

    @property
    def keyauths(self) -> ConsumerAuth:
        return auth_factory(self, "key-auth")

    @property
    def basicauths(self) -> ConsumerAuth:
        return auth_factory(self, "basic-auth")


class Consumers(CrudComponent):
    Entity = Consumer

    async def apply_credentials(self, auths: list[dict], consumer: Consumer) -> None:
        for auth_data in auths:
            auth = auth_factory(consumer, auth_data["type"])
            await auth.create_or_update_credentials(auth_data["config"])

    async def apply_json(self, data: JsonType, clear: bool = True) -> list:
        if not isinstance(data, list):
            data = [data]
        result = []
        for entry in data:
            if not isinstance(entry, dict):
                raise KongError("dictionary required")
            entry = entry.copy()
            groups = entry.pop("groups", [])
            auths = entry.pop("auths", [])
            udata = entry.copy()
            id_ = udata.pop("id", None)
            username = None
            if not id_:
                username = udata.pop("username", None)
                if not username:
                    raise KongError("Consumer username or id is required")
            uid = cast(str, id_ or username)
            try:
                entity = await self.get(uid)
            except KongResponseError as exc:
                if exc.status == 404:
                    entity = await self.create(**entry)
                else:
                    raise
            else:
                if entry:
                    entity = await self.update(uid, **udata)
            consumer = cast(Consumer, entity)
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
