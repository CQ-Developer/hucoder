from collections.abc import Iterable
from numbers import Number
from typing import Any, Mapping


def dict_to_dataclass[T](d: dict[str, Any], t: type[T]) -> T | None:
    pass


def clean_dict(d: Any) -> Any:
    if isinstance(d, (str, bytes, bytearray, Number)):
        return d
    if isinstance(d, Mapping):
        return {k: clean_dict(v) for k, v in d.items() if v is not None}
    if isinstance(d, Iterable):
        _d = [clean_dict(e) for e in d if e is not None]
        if isinstance(d, set):
            return set(_d)
        if isinstance(d, tuple):
            return tuple(_d)
        return _d
    return d
