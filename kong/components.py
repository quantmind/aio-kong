import asyncio


class Component:

    def __init__(self, root: object, name: str = None) -> None:
        self.root = root
        self.name = name or self.__class__.__name__.lower()

    def __repr__(self) -> str:
        return self.url

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def cli(self):
        return self.root.cli

    @property
    def url(self) -> str:
        return '%s/%s' % (self.root.url, self.name)

    def execute(self, url: str, method: str=None, **params) -> object:
        return self.root.execute(url, method, **params)

    def apply_json(self, data):
        raise NotImplementedError


class CrudComponent(Component):

    def get_list(self, **params):
        return self.execute(self.url, params=params, wrap=self.wrap_list)

    def get(self, id):
        return self.execute('%s/%s' % (self.url, id), wrap=self.wrap)

    def has(self, id):
        return self.execute('%s/%s' % (self.url, id), 'head',
                            callback=self.head)

    def create(self, skip_error=None, **params):
        return self.execute(self.url, 'post', json=params,
                            wrap=self.wrap, skip_error=skip_error)

    def update(self, id, **params):
        url = '%s/%s' % (self.url, id)
        return self.execute(url, 'patch', json=params, wrap=self.wrap)

    def delete(self, id):
        return self.execute('%s/%s' % (self.url, id), 'delete')

    def wrap_list(self, data):
        return [self.wrap(d) for d in data['data']]

    def wrap(self, data):
        return data

    def head(self, response):
        if response.status_code == 404:
            return False
        elif response.status_code == 200:
            return True
        else:
            response.raise_for_status()


class Services(CrudComponent):
    """Kong API component"""
    def wrap(self, data):
        return Service(self, data)

    async def apply_json(self, data):
        """Apply a JSON data object for a service
        """
        name = data.get('name')
        if not name:
            raise ValueError('name is required')
        config = data.get('config')
        if not config:
            raise ValueError('config dictionary for %s is required' % name)

        if await self.has('name'):
            await self.update(name, **config)
        else:
            await self.create(name=name, **config)


class Consumers(CrudComponent):

    def wrap(self, data):
        return Consumer(self, data)


class Certificates(CrudComponent):
    """Kong TLS certificate component"""

    def wrap(self, data):
        return Certificate(self, data)


class KongEntity:

    def __init__(self, root, data):
        self.root = root
        self.data = data

    @property
    def cli(self):
        return self.root.cli

    @property
    def id(self):
        return self.data['id']

    @property
    def url(self):
        return '%s/%s' % (self.root.url, self.id)

    def __repr__(self):
        return repr(self.data)

    def execute(self, url, method=None, **params):
        return self.root.execute(url, method, **params)


class Service(KongEntity):
    """Object representing a service
    """
    @property
    def plugins(self):
        return Plugins(self)

    @property
    def routes(self):
        return ServiceRoutes(self, 'routes')

    @property
    def name(self):
        return self.data['name']

    @property
    def host(self):
        return self.data.get('host')

    def delete(self):
        return self.root.delete(self.id)


class Plugins(CrudComponent):
    pass


class ServiceRoutes(CrudComponent):
    """Routes associates with a service
    """
    @property
    def url(self) -> str:
        return '%s/%s' % (self.cli.url, self.name)

    def get_list(self, **params):
        url = '%s/%s' % (self.root.url, self.name)
        return self.execute(url, params=params, wrap=self.wrap_list)

    def create(self, skip_error=None, **params):
        params['service'] = dict(id=self.root.id)
        return self.execute(self.url, 'post', json=params,
                            wrap=self.wrap, skip_error=skip_error)

    async def delete_all(self):
        coros = [self.delete(r['id']) for r in await self.get_list()]
        if coros:
            await asyncio.gather(*coros)
            return len(coros)
        return 0


class Consumer(KongEntity):

    @property
    def username(self):
        return self.data['username']


class Certificate(KongEntity):

    def add_sni(self, host):
        pass
