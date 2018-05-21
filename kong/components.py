from itertools import zip_longest

from .utils import as_list


class KongError(Exception):

    def __init__(self, response, msg=''):
        super().__init__(msg)
        self.response = response

    @property
    def status(self):
        return self.response.status


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
        return self.execute('%s/%s' % (self.url, id), 'get',
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

    async def head(self, response):
        if response.status == 404:
            return False
        elif response.status == 200:
            return True
        else:
            raise KongError(response)


class Services(CrudComponent):
    """Kong API component"""
    def wrap(self, data):
        return Service(self, data)

    async def remove(self, id):
        print('getting %s' % id)
        s = await self.get(id)
        print('removing %s routes' % id)
        await s.routes.delete_all()
        print('removing %s' % id)
        await self.delete(id)

    async def apply_json(self, data):
        """Apply a JSON data object for a service
        """
        name = data.get('name')
        if not name:
            raise ValueError('name is required')
        config = data.get('config')
        if not config:
            raise ValueError('config dictionary for %s is required' % name)

        if await self.has(name):
            srv = await self.update(name, **config)
        else:
            srv = await self.create(name=name, **config)

        srv.data['routes'] = await srv.routes.apply_json(
            data.get('routes') or {}
        )

        return srv


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
        routes = await self.get_list()
        for route in routes:
            await self.delete(route['id'])
        return len(routes)

    async def apply_json(self, data):
        if not isinstance(data, list):
            data = [data]
        routes = await self.get_list()
        result = []
        for d, route in zip_longest(data, routes):
            if not d:
                if route:
                    await self.delete(route['id'])
                continue
            as_list('hosts', d)
            as_list('paths', d)
            as_list('methods', d)
            if not route:
                route = await self.create(**d)
            else:
                route = await self.update(route['id'], **d)
            result.append(route)
        return result


class Consumer(KongEntity):

    @property
    def username(self):
        return self.data['username']


class Certificate(KongEntity):

    def add_sni(self, host):
        pass
