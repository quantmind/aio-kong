from .components import CrudComponent, KongEntity


class Consumers(CrudComponent):

    def wrap(self, data):
        return Consumer(self, data)


class Consumer(KongEntity):

    @property
    def username(self):
        return self.data['username']
