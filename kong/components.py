import json

from .utils import as_params, as_dict, uid


class KongError(Exception):
    pass


class KongResponseError(KongError):
    def __init__(self, response, message=''):
        self.response = response
        self.message = as_dict(message, 'message')
        self.message['request_url'] = str(response.url)
        self.message['request_method'] = response.method
        self.message['response_status'] = response.status

    @property
    def status(self):
        return self.response.status

    def __str__(self):
        return json.dumps(self.message, indent=4)


class KongEntity:
    """A Kong entity is either a

    - Service
    - Route
    - Plugin
    - Consumer
    - Certificate
    - SNI
    """
    def __init__(self, root, data):
        self.root = root
        self.data = data

    def __repr__(self) -> str:
        return repr(self.data)

    def __str__(self) -> str:
        return self.__repr__()

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    @property
    def cli(self):
        return self.root.cli

    @property
    def id(self):
        return self.data['id']

    @property
    def name(self):
        return self.data.get('name', '')

    @property
    def url(self):
        return '%s/%s' % (self.root.url, self.id)

    def get(self, item, default=None):
        return self.data.get(item, default)

    def execute(self, url, method=None, **params):
        return self.root.execute(url, method, **params)


class CrudComponent:
    Entity = KongEntity

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
        return f'{self.cli.url}/{self.name}'

    @property
    def is_entity(self):
        return isinstance(self.root, KongEntity)

    def execute(self, url: str, method: str = None, **kwargs) -> object:
        return self.root.execute(url, method, **kwargs)

    def apply_json(self, data):
        raise NotImplementedError

    async def paginate(self, **params):
        url = self.list_create_url()
        next_ = url
        params = as_params(**params)
        while next_:
            if not next_.startswith(url):
                next_ = f'{url}?{next_.split("?")[1]}'
            data = await self.execute(next_, params=params)
            next_ = data.get('next')
            for d in data['data']:
                yield self.wrap(d)

    def get_list(self, **params):
        url = self.list_create_url()
        return self.execute(
            url, params=as_params(**params), wrap=self.wrap_list
        )

    async def get_full_list(self, **params):
        return [d async for d in self.paginate(**params)]

    def get(self, id_):
        url = f'{self.url}/{uid(id_)}'
        return self.execute(url, wrap=self.wrap)

    def has(self, id_):
        url = f'{self.url}/{uid(id_)}'
        return self.execute(url, 'get', callback=self.head)

    def create(self, **params):
        url = self.list_create_url()
        return self.execute(url, 'post', json=params, wrap=self.wrap)

    def update(self, id_, **params):
        url = f'{self.url}/{uid(id_)}'
        return self.execute(url, 'patch', json=params, wrap=self.wrap)

    def delete(self, id_):
        url = f'{self.url}/{uid(id_)}'
        return self.execute(url, 'delete')

    async def delete_all(self) -> int:
        n = 0
        async for entity in self.paginate():
            await self.delete(entity.id)
            n += 1
        return n

    async def head(self, response):
        if response.status == 404:
            return False
        elif response.status == 200:
            return True
        else:   # pragma: no cover
            raise KongResponseError(response)

    def wrap(self, data):
        return self.Entity(self, data)

    def wrap_list(self, data):
        return [self.wrap(d) for d in data['data']]

    def list_create_url(self) -> str:
        if self.is_entity:
            return f'{self.root.url}/{self.name}'
        else:
            return self.url
