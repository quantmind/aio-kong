import os
import sys
from aiohttp import ClientResponse, ClientSession
from typing import Any, Callable, Dict, Optional

from . import __version__
from .certificates import Certificates
from .components import CrudComponent, KongError, KongResponseError
from .consumers import Consumers
from .plugins import Plugins
from .routes import Routes
from .services import Services
from .snis import Snis

__all__ = ["Kong", "KongError", "KongResponseError"]

DEFAULT_USER_AGENT = (
    f"Python/${'.'.join(map(str, sys.version_info[:2]))} aio-kong/${__version__}"
)


class Kong:
    """Kong client"""

    url: str = os.getenv(
        "KONG_ADMIN_URL", os.getenv("KONG_URL", "http://127.0.0.1:8001")
    )
    content_type: str = "application/json, text/*; q=0.5"

    def __init__(
        self,
        url: str = None,
        session: Optional[ClientSession] = None,
        request_kwargs: Optional[Dict] = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.url = url or self.url
        self.session = session
        self.user_agent = user_agent
        self.request_kwargs = request_kwargs or {}
        self.services = Services(self)
        self.routes = Routes(self)
        self.plugins = Plugins(self)
        self.consumers = Consumers(self)
        self.certificates = Certificates(self)
        self.acls = CrudComponent(self, "acls")
        self.snis = Snis(self)

    def __repr__(self) -> str:
        return self.url

    __str__ = __repr__

    @property
    def cli(self) -> "Kong":
        return self

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def __aenter__(self) -> object:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def execute(
        self,
        url: str,
        method: str = "",
        headers: Optional[Dict[str, str]] = None,
        callback: Optional[Callable[[ClientResponse], Any]] = None,
        wrap: Optional[Callable[[Any], Any]] = None,
        timeout=None,
        **kw,
    ) -> Any:
        if not self.session:
            self.session = ClientSession()
        method = method or "GET"
        headers_ = self.default_headers()
        headers_.update(headers or ())
        kw.update(self.request_kwargs)
        response = await self.session.request(method, url, headers=headers_, **kw)
        if callback:
            return await callback(response)
        if response.status == 204:
            return True
        if response.status >= 400:
            try:
                data = await response.json()
            except Exception:
                data = await response.text()
            raise KongResponseError(response, data)
        response.raise_for_status()
        data = await response.json()
        return wrap(data) if wrap else data

    async def apply_json(self, config: Dict, clear: bool = True):
        if not isinstance(config, dict):
            raise KongError("Expected a dict got %s" % type(config).__name__)
        result = {}
        for name, data in config.items():
            if not isinstance(data, list):
                data = [data]
            o = getattr(self, name)
            if not o:
                raise KongError("Kong object %s not available" % name)
            result[name] = await o.apply_json(data, clear=clear)
        return result

    async def delete_all(self) -> None:
        await self.services.delete_all()
        await self.consumers.delete_all()
        await self.plugins.delete_all()
        await self.certificates.delete_all()

    def default_headers(self) -> Dict[str, str]:
        return {"user-agent": self.user_agent, "accept": self.content_type}
