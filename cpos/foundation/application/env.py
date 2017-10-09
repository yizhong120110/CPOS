#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Descriptions
"""
import threading
import copy
import time
from ..substrate.interfaces import *

__________FW__________ = {}
__________FW__________GUARD = threading.RLock()


def env_get(key, value=''):
    with __________FW__________GUARD:
        v = __________FW__________.get(key)
        if v == None:
            __________FW__________[key] = copy.deepcopy(value)
            return value
        return copy.deepcopy(v)


def env_set(key, value):
    with __________FW__________GUARD:
        __________FW__________[key] = copy.deepcopy(value)


def env_clone():
    with __________FW__________GUARD:
        return copy.deepcopy(__________FW__________)


def env_pop(key, value=''):
    with __________FW__________GUARD:
        v = __________FW__________.get(key)
        if v == None:
            return value
        return __________FW__________.pop(key)


if __name__ == '__main__':
    env_set('k', 'v')
    print(env_pop('k'))
