# Async Python Client for Kong

[![PyPI version](https://badge.fury.io/py/aio-kong.svg)](https://badge.fury.io/py/aio-kong)
[![Python versions](https://img.shields.io/pypi/pyversions/aio-kong.svg)](https://pypi.org/project/aio-kong)
[![CircleCI](https://circleci.com/gh/quantmind/aio-kong.svg?style=svg)](https://circleci.com/gh/quantmind/aio-kong)
[![codecov](https://codecov.io/gh/quantmind/aio-kong/branch/master/graph/badge.svg)](https://codecov.io/gh/quantmind/aio-kong)

Tested with [kong][] v1.0.x

## Installation & Testing

To install the package
```
pip install aio-kong
```
To run tests, clone and
```
./dev/install.sh
pytest --cov
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
    print(json.dumps(services, indent=4))
```
The client has handlers for all Kong objects

* ``cli.services`` CRUD operations on services
* ``cli.routes`` CRUD operations on routes
* ``cli.plugins`` CRUD operations on plugins
* ``cli.consumers`` CRUD operations on consumers
* ``cli.consumers`` CRUD operations on consumers
* ``cli.certificates`` CRUD operations on TLS certificates
* ``cli.snis`` CRUD operations on SNIs
* ``cli.acls`` To list all ACLs

### Apply a configuration

The client allow to apply a configuration object to kong:
```python
await cli.apply_json(config)
```

## Command line tool

The library install the ``kong`` command line tool for uploading kong configuration files.
```
kong --yaml config.yaml
```

[kong]: https://docs.konghq.com
