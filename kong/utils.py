import socket
from multidict import MultiDict
from typing import Any
from uuid import UUID


def as_list(key: str, data: dict) -> dict:
    if key in data:
        v = data[key]
        if isinstance(v, str):
            v = [v]
        data[key] = list(v)
    return data


def as_dict(data: Any, key: str = "data") -> dict:
    return {key: data} if not isinstance(data, dict) else data


def local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    try:
        return s.getsockname()[0]
    finally:
        s.close()


def as_params(*, params: dict | None = None, **kwargs: Any) -> MultiDict:
    mp: MultiDict = MultiDict(params if params is not None else {})
    mp.update(kwargs)
    return mp


def uid(id_: str | UUID) -> str:
    if isinstance(id_, UUID):
        return str(id_)
    try:
        return str(UUID(id_))
    except ValueError:
        return str(id_)
