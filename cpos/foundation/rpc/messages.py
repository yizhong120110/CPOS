#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Descriptions
"""
import pickle
import json
import uuid
from ..substrate.interfaces import *
from ..substrate.utils.logger import logger


class RPCMessage(Monitored):

    '''Base class of rpc messages.

    '''
    NAME = 'RPCMessage'
    __slots__ = ('_data',)

    def __init__(self, content, exchange, routing_key):
        '''Init message with exchange , routing_key and content.

        '''

        super(RPCMessage, self).__init__()
        self._data = {'exchange': '', 'routing_key': '', 'content': {}}
        self._data['exchange'] = exchange
        self._data['routing_key'] = routing_key

        self.setcontent(content)

    def serialize(self):
        '''Implementation of Monitored

        '''
        return str(self._data)

    def getexchange(self):
        return str(self._data['exchange'])

    def setexchange(self, exchange):
        self._data['exchange'] = exchange

    def get_routing_key(self):
        return str(self._data['routing_key'])

    def set_routing_key(self, routing_key):
        self._data['routing_key'] = routing_key

    def _dict_to_content(self, s):
        try:
            self._data['content'] = pickle.dumps(s)
        except ValueError as err:
            logger.oes("", lv='error', cat='esb.rpc')
            return

        pass

    def _string_to_content(self, s):
        try:
            self._data['content'] = pickle.dumps(s)
        except ValueError as err:
            logger.oes("", lv='error', cat='esb.rpc')
            return

    def _bytes_to_content(self, s):

        try:
            self._data['content'] = s
        except ValueError as err:
            logger.oes("", lv='error', cat='esb.rpc')
            return

    def get_content_raw(self):
        return self._data['content']

    def getcontent(self):
        '''Get content.

        '''
        try:
            return pickle.loads(self._data['content'])
        except pickle.PickleError as e:
            return self._data['content']

    def setcontent(self, content):
        '''Set content.

            Accept parameter in both string and dic formats.
        '''
        if isinstance(content, dict):
            self._dict_to_content(content)
            return True
        elif isinstance(content, str):
            self._string_to_content(content)
            return True
        elif isinstance(content, bytes) or isinstance(content, bytearray):
            self._bytes_to_content(content)
            return True

        logger.ods("[setcontent] only accepts DICT,STR,BYTES/BYTEARRAY",
                   lv='error', cat='esb.rpc')
        return False


class Request(RPCMessage):

    '''Request class of rpc messages.

        Derived from RPCMessage
    '''
    NAME = 'Request'
    __slots__ = ('_data',)

    def __init__(self, content, exchange, routing_key, timeout_time=-1):
        '''Init message with exchange , routing_key ,content and timeout time.

            Same initializer as RPCMessage, but allowed to set timeout value additionally.
        '''
        super(Request, self).__init__(content, exchange, routing_key)

        self._data['correlation_id'] = uuid.uuid4().hex
        self._data['timeout_time'] = timeout_time

        # 'respond' reserved for client objects which will store the RECEIVED data into it.
        self._data['respond'] = None

    def getrespond(self):
        '''Get the respond after calling the Client objects to send this request.

        '''
        return self._data['respond']

    def setrespond(self, respond):
        '''Client ojbects will use this method to bind the respond to this request.

        '''
        self._data['respond'] = respond

    def get_correlation_id(self):
        return str(self._data['correlation_id'])

    def set_correlation_id(self, correlation_id):
        self._data['correlation_id'] = correlation_id

    def get_timeout_time(self):
        return self._data['timeout_time']

    def set_timeout_time(self, timeout):
        self._data['timeout_time'] = timeout


# readonly
class Received(RPCMessage):

    '''RPC server or client(reply mode) use this class to wrap message.

        Provide read-only methods to get reply_to queue name and correlation_id.

    '''

    NAME = 'Received'
    __slots__ = ('_data',)

    def __init__(self, content, exchange, routing_key, reply_to, correlation_id):
        super(Received, self).__init__(content, exchange, routing_key)

        self._data['reply_to'] = reply_to
        self._data['correlation_id'] = correlation_id

    def get_reply_to(self):
        return self._data['reply_to']

    def get_correlation_id(self):
        return self._data['correlation_id']


class Reply(Request):

    '''RPC server use this class to build up a reply message.

        Provide a initializer that convert a RECEIVED object into a Request

    '''
    NAME = 'Reply'
    __slots__ = ('_data',)

    def __init__(self, content, received):
        super(Reply, self).__init__(content, '', received.get_reply_to())
        self._data['correlation_id'] = received.get_correlation_id()


class RequestManager(object):

    def __init__(self, requests):
        self.requests = requests

    def total_requests(self):
        return len(self.requests)

    def total_responds(self):
        tr = 0
        for r in self.requests:
            if r.getrespond() is not None:
                tr += 1
        return tr

    def total_failures(self):
        return self.total_requests() - self.total_responds()

    def succeeded_requests(self):
        srl = []
        for r in self.requests:
            if r.getrespond() is not None:
                srl.append(r)
        return srl
