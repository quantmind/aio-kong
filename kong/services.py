from typing import List

from .components import CrudComponent, JsonType, KongError
from .plugins import KongEntityWithPlugins
from .routes import Routes
from .utils import local_ip

REMOVE = frozenset(("absent", "remove"))
LOCAL_HOST = frozenset(("localhost", "127.0.0.1"))


class Service(KongEntityWithPlugins):
    """Object representing a Kong service"""

    @property
    def routes(self) -> Routes:
        return Routes(self)

    @property
    def host(self) -> str:
        return self.data.get("host")


class Services(CrudComponent):
    """Kong Services"""

    Entity = Service

    async def delete(self, id_):
        srv = self.wrap({"id": id_})
        await srv.routes.delete_all()
        await srv.plugins.delete_all()
        return await super().delete(id_)

    async def apply_json(self, data: JsonType, clear: bool = True) -> List[Service]:
        """Apply a JSON data objects for services"""
        if not isinstance(data, list):
            data = [data]
        result = []
        for entry in data:
            if not isinstance(entry, dict):
                raise KongError("dictionary required")
            entry = entry.copy()
            ensure = entry.pop("ensure", None)
            name = entry.pop("name", None)
            id_ = entry.pop("id", None)
            id_or_name = name or id_
            routes = entry.pop("routes", [])
            plugins = entry.pop("plugins", [])
            host = entry.pop("host", None)
            if host in LOCAL_HOST:
                host = local_ip()
            if ensure in REMOVE:
                if not id_or_name:
                    raise KongError(
                        "Service name or id is required to remove previous services"
                    )
                if await self.has(id_or_name):
                    await self.delete(id_or_name)
                continue
            entry.update(host=host)
            if id_or_name and await self.has(id_or_name):
                if id_ and name:
                    entry.update(name=name)
                srv = await self.update(id_or_name, **entry)
            else:
                if name:
                    entry.update(name=name)
                srv = await self.create(**entry)
            srv.data["routes"] = await srv.routes.apply_json(routes)
            srv.data["plugins"] = await srv.plugins.apply_json(plugins)
            result.append(srv)
        return result
