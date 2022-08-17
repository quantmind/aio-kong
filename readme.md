# Async Python Client for Kong

[![PyPI version](https://badge.fury.io/py/aio-kong.svg)](https://badge.fury.io/py/aio-kong)
[![Python versions](https://img.shields.io/pypi/pyversions/aio-kong.svg)](https://pypi.org/project/aio-kong)
[![Build](https://github.com/quantmind/aio-kong/workflows/build/badge.svg)](https://github.com/quantmind/aio-kong/actions?query=workflow%3Abuild)
[![codecov](https://codecov.io/gh/quantmind/aio-kong/branch/master/graph/badge.svg)](https://codecov.io/gh/quantmind/aio-kong)
[![Downloads](https://img.shields.io/pypi/dd/aio-kong.svg)](https://pypi.org/project/aio-kong/)


Tested with [kong][] v2.8

## Installation & Testing

To install the package

```
pip install aio-kong
```

To run tests, clone and

```
make test
```

:warning: If you don't have Kong or postgres running locally, run the services first

```bash
make services
```

test certificates were generated using the command

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -nodes -subj '/CN=localhost'
```

## Client

The client can be imported via

```python
from kong.client import Kong
```

In a coroutine:

```python
async with Kong() as cli:
    services = await cli.services.get_list()
    print(json.dumps([s.data for s in services], indent=2))
```

By default the url is obtained from the "KONG_ADMIN_URL" environment variable which defaults to http://127.0.0.1:8001.

The client has handlers for all Kong objects

- [cli.services](./kong/services.py) CRUD operations on services
- [cli.routes](./kong/routes.py) CRUD operations on routes
- [cli.plugins](./kong/plugins.py) CRUD operations on plugins
- [cli.consumers](./kong/consumers.py) CRUD operations on consumers
- [cli.certificates](./kong/certificates.py) CRUD operations on TLS certificates
- [cli.snis](./kong/snis.py) CRUD operations on SNIs
- `cli.acls` To list all ACLs

### Apply a configuration

The client allow to apply a configuration object to kong:

```python
await cli.apply_json(config)
```

## Command line tool

The library install the `kongfig` command line tool for uploading kong configuration files.

```
kongfig --yaml config.yaml
```

[kong]: https://github.com/Kong/kong
