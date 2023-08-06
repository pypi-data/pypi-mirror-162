# -*- coding: UTF-8 -*-

from collections import namedtuple
from decimal import Decimal
from os import makedirs
from os.path import isdir, realpath, dirname
from re import compile
from typing import Any, Union, Match


def single_quote(value: Any) -> Any:
    if isinstance(value, str):
        return f"'{value}'"
    return value


def clean_string(target: str, text: str) -> str:
    results = find_substring(target, text)

    if results is not None:
        start, end = results
        space = start - 1
        comma = space - 1

        if text[comma:space] == ",":
            return text.replace(text[comma:end], "")
        elif text[space:start] == " ":
            return text.replace(text[space:end], "")
        else:
            return text.replace(text[start:end], "")

    return text.strip(" ")


def find_substring(target: str, text: str) -> tuple:
    result = text.find(target)

    if result != -1:
        return result, result + len(target)


def find_in_file(file_path: str, target_name: str, pattern: str) -> list[str]:
    group: str = re_group(target_name, pattern)

    with open(file_path, "r", encoding="UTF-8") as fh:
        text: str = fh.read()
        matches = re_search(text, group)

        if len(matches) > 0:
            return [item.group(target_name) for item in matches]


def re_search(text: str, pattern: str) -> list[Match[str]]:
    template = compile(pattern)
    return [item for item in template.finditer(text)]


def re_group(name: str, pattern: str) -> str:
    return fr"(?P<{name}>{pattern})"


def ensure_folder(path: str):
    """Read the file path and recursively create the folder structure if needed."""
    folder_path: str = dirname(realpath(path))
    make_dirs(folder_path)


def make_dirs(path: str):
    """Checks if a folder path exists and creates it if not."""
    if isdir(path) is False:
        makedirs(path)


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


def to_bytes(value: Union[Decimal, bytes], encoding: str = "UTF-8") -> bytes:
    if isinstance(value, Decimal):
        return encode(str(value), encoding)
    return value


def to_decimal(value: Union[bytes, Decimal], encoding: str = "UTF-8") -> Decimal:
    if isinstance(value, bytes):
        return Decimal(decode(value, encoding))
    return value


def as_namedtuple(name: str, **kwargs):
    if len(kwargs) > 0:
        return namedtuple(name, kwargs.keys())(**kwargs)
