# -*- coding: UTF-8 -*-

from ast import literal_eval
from os import makedirs
from os.path import dirname, realpath, isdir


def evaluate(value: str):
    """Transform a string to an appropriate data type."""
    try:
        value = literal_eval(value)
    except (SyntaxError, ValueError):
        pass
    return value


def ensure_folder(path: str):
    """Read the file path and recursively create the folder structure if needed."""
    folder_path: str = dirname(realpath(path))
    make_dirs(folder_path)


def make_dirs(path: str):
    """Checks if a folder path exists and creates it if not."""
    if isdir(path) is False:
        makedirs(path)
