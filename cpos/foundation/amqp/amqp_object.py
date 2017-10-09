#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""
from ..substrate.interfaces import *

class AMQPObject(Clarified):
    NAME = 'AMQPObject'


class Class(AMQPObject):
    NAME = 'Unextended Class'


class Method(AMQPObject):
    NAME = 'Unextended Method'
    synchronous = False

    def _set_content(self, properties, body):
        self._properties = properties
        self._body = body

    def get_properties(self):
        return self._properties

    def get_body(self):
        return self._body


class Properties(AMQPObject):
    NAME = 'Unextended Properties'
