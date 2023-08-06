# -*- coding: UTF-8 -*-

def del_prefix(target: str, prefix: str):
    """
    If `target` starts with the `prefix` string and `prefix` is not empty,
    return string[len(prefix):].
    Otherwise, return a copy of the original string.
    """
    if (len(prefix) > 0) and (target.startswith(prefix) is True):
        try:  # python >= 3.9
            target = target.removeprefix(prefix)
        except AttributeError:  # python <= 3.7
            target = target[len(prefix):]

    return target


def del_suffix(target: str, suffix: str):
    """
    If `target` ends with the `suffix` string and `suffix` is not empty,
    return string[:-len(suffix)].
    Otherwise, return a copy of the original string.
    """
    if (len(suffix) > 0) and (target.endswith(suffix) is True):
        try:  # python >= 3.9
            target = target.removesuffix(suffix)
        except AttributeError:  # python <= 3.7
            target = target[:-len(suffix)]

    return target
