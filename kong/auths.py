from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .components import CrudComponent, KongEntity

if TYPE_CHECKING:
    from .consumers import Consumer


def auth_factory(consumer: Consumer, auth_type: str) -> ConsumerAuth:
    known_types = {"basic-auth": BasicAuth, "key-auth": KeyAuth}
    constructor = known_types.get(auth_type, ConsumerAuth)
    return constructor(consumer, auth_type)


class ConsumerAuth(CrudComponent):

    unique_field: str = ""

    @property
    def url(self) -> str:
        return f"{self.root.url}/{self.name}"

    async def get_existing_id(self, creds_config: dict) -> str | None:
        if not self.unique_field:
            raise NotImplementedError(
                "Existence check not implemented for this type of\
                 authentication"
            )
        cur_unique = creds_config[self.unique_field]
        try:
            return next(
                cred
                for cred in await self.get_list()
                if cred[self.unique_field] == cur_unique
            )["id"]
        except StopIteration:
            return None

    async def create_or_update_credentials(self, creds_config: dict) -> KongEntity:
        if existing_id := await self.get_existing_id(creds_config):
            return await self.update_credentials(existing_id, data=creds_config)
        else:
            return await self.create_credentials(data=creds_config)

    async def update_credentials(self, id_: str, **kw: Any) -> KongEntity:
        url = f"{self.url}/{id_}"

        return await self.cli.execute(
            url,
            "patch",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            wrap=self.wrap,
            **kw,
        )

    async def create_credentials(self, **kw: Any) -> KongEntity:
        return await self.cli.execute(
            self.url,
            "post",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            wrap=self.wrap,
            **kw,
        )

    async def get_or_create(self) -> KongEntity:
        secrets = await self.get_list(limit=1)
        return secrets[0] if secrets else await self.create()


class BasicAuth(ConsumerAuth):
    unique_field = "username"


class KeyAuth(ConsumerAuth):
    unique_field = "key"
