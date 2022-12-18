from .components import CrudComponent, KongEntity
from .snis import Snis


class Certificate(KongEntity):
    @property
    def snis(self) -> Snis:
        return Snis(self)


class Certificates(CrudComponent):
    """Kong TLS certificate component"""

    Entity = Certificate
