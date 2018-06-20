# Async Python Client for Kong

[![PyPI version](https://badge.fury.io/py/aio-kong.svg)](https://badge.fury.io/py/aio-kong)

[![CircleCI](https://circleci.com/gh/lendingblock/aio-kong.svg?style=svg)](https://circleci.com/gh/lendingblock/aio-kong)

[![codecov](https://codecov.io/gh/lendingblock/aio-kong/branch/master/graph/badge.svg)](https://codecov.io/gh/lendingblock/aio-kong)


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
## Client

The client can be imported via
```python
from kong.client import Kong
```

In a coroutine::
```python
async with Kong() as cli:
    services = await cli.services.get_list()
    print(json.dumps(services, indent=4))
```

## Command line tool

The library install the ``kong`` command line tool for uploading kong configuration files.
```
kong --yaml config.yaml
```
