from .components import CrudComponent, KongEntity
from .snis import Sni, Snis


class Certificate(KongEntity):
    @property
    def snis(self) -> Snis:
        return Snis(self, Sni)


class Certificates(CrudComponent[Certificate]):
    """Kong TLS certificate component"""
