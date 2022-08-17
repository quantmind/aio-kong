import socket
from multidict import MultiDict
from typing import Any, Dict, Optional, Union
from uuid import UUID


def as_list(key: str, data: Dict) -> Dict:
    v = data.get(key)
    if isinstance(v, str):
        v = [v]
    elif not isinstance(v, list):
        v = []
    data[key] = v
    return data


def as_dict(data: Any, key: str = "data") -> Dict:
    return {key: data} if not isinstance(data, dict) else data


def local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    try:
        return s.getsockname()[0]
    finally:
        s.close()


def as_params(*, params: Optional[Dict] = None, **kwargs: Dict) -> MultiDict:
    mp: MultiDict = MultiDict(params if params is not None else {})
    mp.update(kwargs)
    return mp


def uid(id_: Union[str, UUID]) -> str:
    try:
        return str(UUID(id_))
    except ValueError:
        return str(id_)
