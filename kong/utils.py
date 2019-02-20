import socket
from uuid import UUID
from multidict import MultiDict


def as_list(key, data):
    v = data.get(key)
    if isinstance(v, str):
        v = [v]
    elif not isinstance(v, list):
        v = []
    data[key] = v
    return data


def as_dict(data, key='data'):
    return {key: data} if not isinstance(data, dict) else data


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    try:
        return s.getsockname()[0]
    finally:
        s.close()


def as_params(*, params=None, **kwargs):
    params = MultiDict(params if params is not None else {})
    params.update(kwargs)
    return params


def uid(id_):
    try:
        return str(UUID(id_))
    except ValueError:
        return id_
