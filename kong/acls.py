from .components import CrudComponent, KongEntity


class Acls(CrudComponent):
    """Kong API component"""
    def wrap(self, data):
        return Acl(self, data)


class Acl(KongEntity):
    """Object representing a acl
    """
