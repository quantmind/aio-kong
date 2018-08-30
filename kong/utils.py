import socket
from multidict import MultiDict


def as_list(key, data):
    v = data.get(key)
    if isinstance(v, str):
        v = [v]
    elif not isinstance(v, list):
        v = []
    data[key] = v
    return data


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
