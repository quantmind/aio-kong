

class KongError(Exception):
    pass


class KongResponseError(KongError):
    def __init__(self, response, message=''):
        self.response = response
        self.message = message

    @property
    def status(self):
        return self.response.status

    def __str__(self):
        return f'{self.response.status}: {self.message}'


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
            raise KongResponseError(response)


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


class ServiceEntity(CrudComponent):

    @property
    def url(self) -> str:
        return '%s/%s' % (self.cli.url, self.name)

    def get_list(self, **params):
        url = '%s/%s' % (self.root.url, self.name)
        return self.execute(url, params=params, wrap=self.wrap_list)

    async def delete_all(self):
        routes = await self.get_list()
        for route in routes:
            await self.delete(route['id'])
        return len(routes)
