#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Descriptions
"""


class SJRPCException(Exception):
    pass


class SJRPCExceptionTimeout(SJRPCException):
    pass


class SJRPCExceptionBadCall(SJRPCException):
    pass


class SJRPCExceptionRtError(SJRPCException):
    pass
