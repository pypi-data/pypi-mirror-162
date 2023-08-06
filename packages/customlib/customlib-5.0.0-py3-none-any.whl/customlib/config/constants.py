# -*- coding: UTF-8 -*-

from sys import modules
from weakref import WeakValueDictionary

MODULE = modules.get("__main__")
INSTANCES = WeakValueDictionary()
