from __future__ import annotations

import json
from aiohttp import ClientResponse
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterator, Mapping

from .utils import UUID, as_dict, as_params, uid

if TYPE_CHECKING:
    from .client import Kong


JsonType = dict | list


class KongError(Exception):
    pass


class KongResponseError(KongError):
    def __init__(self, response: ClientResponse, message: str = "") -> None:
        self.response = response
        self.message = as_dict(message, "message")
        self.message["request_url"] = str(response.url)
        self.message["request_method"] = response.method
        self.message["response_status"] = response.status

    @property
    def status(self) -> int:
        return self.response.status

    def __str__(self) -> str:
        return json.dumps(self.message, indent=4)


class KongEntity(Mapping[str, Any]):
    """A Kong entity is either a

    - Service
    - Route
    - Plugin
    - Consumer
    - Certificate
    - SNI
    """

    def __init__(self, root: Kong | CrudComponent, data: dict[str, Any]) -> None:
        self.root = root
        self.data = data

    def __repr__(self) -> str:
        return repr(self.data)

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[str]:
        return iter(self.data)

    def __getitem__(self, item: Any) -> Any:
        return self.data[item]

    def __contains__(self, item: Any) -> bool:
        return item in self.data

    @property
    def cli(self) -> Kong:
        return self.root.cli

    @property
    def id(self) -> str:
        return self.data["id"]

    @property
    def name(self) -> str:
        return self.data.get("name") or ""

    @property
    def url(self) -> str:
        return "%s/%s" % (self.root.url, self.id)

    def get(self, item: Any, default: Any = None) -> Any:
        return self.data.get(item, default)

    async def execute(self, url: str, method: str = "", **params: Any) -> Any:
        return await self.root.execute(url, method, **params)


class CrudComponent:
    Entity = KongEntity

    def __init__(self, root: Kong | KongEntity, name: str = "") -> None:
        self.root = root
        self.name = name or self.__class__.__name__.lower()

    def __repr__(self) -> str:
        return self.url

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def cli(self) -> Kong:
        return self.root.cli

    @property
    def url(self) -> str:
        return f"{self.cli.url}/{self.name}"

    @property
    def is_entity(self) -> bool:
        return isinstance(self.root, KongEntity)

    async def execute(self, url: str, method: str = "", **kwargs: Any) -> Any:
        return await self.root.execute(url, method, **kwargs)

    async def apply_json(self, data: JsonType, clear: bool = True) -> list:
        raise NotImplementedError

    async def paginate(self, **params: Any) -> AsyncIterator[KongEntity]:
        url = self.list_create_url()
        next_ = url
        exec_params = as_params(**params)
        while next_:
            if not next_.startswith(url):
                next_ = f'{url}?{next_.split("?")[1]}'
            data = await self.execute(next_, params=exec_params)
            next_ = data.get("next")
            for d in data["data"]:
                yield self.wrap(d)

    async def get_list(self, **params: Any) -> list[KongEntity]:
        url = self.list_create_url()
        return await self.execute(url, params=as_params(**params), wrap=self.wrap_list)

    async def get_full_list(self, **params: Any) -> list[KongEntity]:
        return [d async for d in self.paginate(**params)]

    async def get(self, id_: str | UUID) -> KongEntity:
        url = f"{self.url}/{uid(id_)}"
        return await self.execute(url, wrap=self.wrap)

    async def has(self, id_: str | UUID) -> bool:
        url = f"{self.url}/{uid(id_)}"
        return await self.execute(url, "get", callback=self.head)

    async def create(self, **params: Any) -> KongEntity:
        url = self.list_create_url()
        return await self.execute(url, "post", json=params, wrap=self.wrap)

    async def update(self, id_: str | UUID, **params: Any) -> KongEntity:
        url = f"{self.url}/{uid(id_)}"
        return await self.execute(url, "patch", json=params, wrap=self.wrap)

    async def delete(self, id_: str | UUID) -> bool:
        url = f"{self.url}/{uid(id_)}"
        return await self.execute(url, "delete")

    async def delete_all(self) -> int:
        n = 0
        async for entity in self.paginate():
            await self.delete(entity.id)
            n += 1
        return n

    async def head(self, response: ClientResponse) -> bool:
        if response.status == 404:
            return False
        elif response.status == 200:
            return True
        else:  # pragma: no cover
            raise KongResponseError(response)

    def wrap(self, data: dict) -> KongEntity:
        return self.Entity(self, data)

    def wrap_list(self, data: dict) -> list[KongEntity]:
        return [self.wrap(d) for d in data["data"]]

    def list_create_url(self) -> str:
        if self.is_entity:
            return f"{self.root.url}/{self.name}"
        else:
            return self.url
