# -*- coding: UTF-8 -*-

from configparser import ExtendedInterpolation

from .cfgparser import CfgParser
from .constants import MODULE, INSTANCES
from .utils import evaluate


def get_config(**kwargs):
    name: str = kwargs.pop('name', MODULE.__name__)

    interpolation = kwargs.pop("interpolation", ExtendedInterpolation())
    converters = kwargs.pop(
        "converters",
        {
            "list": evaluate,
            "tuple": evaluate,
            "set": evaluate,
            "dict": evaluate,
        }
    )

    return _get_config(
        name=name,
        interpolation=interpolation,
        converters=converters,
        **kwargs
    )


def _get_config(name: str, **kwargs):
    name: str = f"{name}.{CfgParser.__name__}"

    if name not in INSTANCES:
        # a strong reference to the object is required.
        instance = CfgParser(**kwargs)
        INSTANCES[name] = instance
    return INSTANCES[name]


__all__ = ["CfgParser", "get_config"]
