# -*- coding: UTF-8 -*-

from typing import Union


def encode(value: Union[str, bytes], encoding: str = "UTF-8") -> bytes:
    """Encode the string `value` with UTF-8."""
    if isinstance(value, str):
        return value.encode(encoding)
    return value


def decode(value: Union[bytes, str], encoding: str = "UTF-8") -> str:
    """Decode the bytes-like object `value` with UTF-8."""
    if isinstance(value, bytes):
        return value.decode(encoding)
    return value
