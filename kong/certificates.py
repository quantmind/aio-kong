from .components import CrudComponent, KongEntity


class Certificates(CrudComponent):
    """Kong TLS certificate component"""

    def wrap(self, data):
        return Certificate(self, data)


class Certificate(KongEntity):

    def add_sni(self, host):
        pass
