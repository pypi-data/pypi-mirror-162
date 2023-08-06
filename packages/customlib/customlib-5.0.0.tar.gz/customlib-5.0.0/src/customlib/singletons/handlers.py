# -*- coding: UTF-8 -*-

from functools import wraps

from .constants import INSTANCES


class MetaSingleton(type):
    """
    Singleton metaclass (for non-strict class).
    Restrict object to only one instance per runtime.
    """

    def __call__(cls, *args, **kwargs):
        if hasattr(cls, "_instance") is False:
            cls._instance = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instance


def singleton(cls):
    """
    Singleton decorator (for metaclass).
    Restrict object to only one instance per runtime.
    """

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in INSTANCES:
            # a strong reference to the object is required.
            instance = cls(*args, **kwargs)
            INSTANCES[cls] = instance
        return INSTANCES[cls]
    return wrapper
