#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Descriptions
"""

import uuid
import datetime
import time

from .exceptions import *
from .messages import *
from .mqservice import *
from .server import *
from ..substrate.interfaces import *
from ..substrate.utils.logger import logger


class BaseClient(Monitored):

    '''Base class for Clients.

    '''

    def __init__(self, connection_pool):
        '''Initialize BaseClient with a given ConnectionPool object.

        '''

        super(BaseClient, self).__init__()
        self.connection_pool = connection_pool
        self.reply_to = None

    def bind_requests(self, request_list):
        '''Bind a Request list to be Processed.

        '''
        self.request_list = request_list

    def before_publish_all(self, connection):
        '''rpc() will call this method just after it getting a free connection from the pool.

            Should be rewritten in the derived classes.

        '''
        pass

    def before_publish(self, connection, request):
        '''rpc() will call this method before publishing a request.

            Should be rewritten in the derived classes.

        '''
        request.setrespond(None)
        pass

    def after_publish(self, connection, request):
        '''rpc() will call this method after publishing a request.

            Should be rewritten in the derived classes.

        '''
        pass

    def after_publish_all(self, connection):
        '''rpc() will call this method after publishing all the requests.

            Should be rewritten in the derived classes.

        '''
        pass

    def get_reply_to(self):
        '''Get a random name for creating the reply_to queue.

            Should be rewritten self.reply_to variable in the derived classes. This method in BaseClient will always return None.

        '''
        return self.reply_to

    def rpc(self):
        '''To make all requests that holds by the client publish.

            Not recommended to rewrite this method.

        '''
        connection = self.connection_pool.get_free_connection()
        try:
            self.before_publish_all(connection)
            for request in self.request_list:
                self.before_publish(connection, request)
                #ods('basic_publish : ' + str(request.serialize()) )
                connection.basic_publish(request, self.get_reply_to())
                self.after_publish(connection, request)

            self.after_publish_all(connection)

        except Exception as err:
            logger.oes("", lv='dev', cat='esb.rpc')
            connection.makesure_alive()
        finally:
            self.connection_pool.recycle_connection(connection)


class SyncClient(BaseClient):

    '''SyncClient for multiple synchronized job.

        Calling rpc() will process each Request objects one by one, and wait for reply messages once after sending a request.
    Package the reply message into a Received object , and bind it to the Request object as Respond.
    It can be retrieved by calling Request.getrespond(). If no respond or timeouted, the Request.getrespond() will return None.


    '''

    def __init__(self, connection_pool):
        '''Initialize SyncClient with a given ConnectionPool object.

            Setup an uuid string to reply_to .
        A single SyncClient object will use the same reply_to queue for all the requests.
        timeout_time is set to -1.

        '''

        super(SyncClient, self).__init__(connection_pool)
        self.reply_to = uuid.uuid4().hex
        self.timeout_time = -1

    def before_publish_all(self, connection):
        '''rpc() will call this method just after it getting a free connection from the pool.

            Declared a reply_to queue here.

        '''
        super(SyncClient, self).before_publish_all(connection)
        connection.queue_declare(self.get_reply_to(), False, True)

    def after_publish_all(self, connection):
        '''rpc() will call this method after publishing all the requests.

            Removed reply_to queue on RabbitMQ server

        '''

        connection.queue_delete(self.get_reply_to())
        # connection.shutdown()
        super(SyncClient, self).after_publish_all(connection)

    def before_publish(self, connection, request):
        '''rpc() will call this method before publishing a request.

            Initialized timeout settings here.

        '''
        super(SyncClient, self).before_publish(connection, request)
        self.timeout_time = request.get_timeout_time()
        self.timeout_start = datetime.datetime.now()

    def after_publish(self, connection, request):
        '''rpc() will call this method after publishing a request.

            Waiting for replys here.

        '''
        connection.basic_consume(self.get_reply_to())
        self._waitfor_reply(connection, request)
        connection.basic_cancel()
        super(SyncClient, self).after_publish(connection, request)

    def _waitfor_reply(self, connection, request):
        '''Wait for reply messages here.


        '''
        res = None
        while True:
            connection.process_data()
            received = connection.pop_received()
            if received is not None:
                if received.get_correlation_id() == request.get_correlation_id():
                    request.setrespond(received)
                    break

            if self._check_timeout():
                request.setrespond(None)
                break

    def _check_timeout(self):
        '''Check Timeout in inner loop.

            If set a Request object timeout_time to -1, it will never timeouted.

        '''

        if self.timeout_time == -1:
            return False
        dt = datetime.datetime.now() - self.timeout_start
        #print ('dt.total_seconds() %s  ---   self.timeout_time %s' %(dt.total_seconds(),self.timeout_time)   )
        timeouted = dt.total_seconds() >= self.timeout_time
        return timeouted


class AsyncClient(SyncClient):

    '''AsyncClient for multiple asynchronized job.

        It will process every Request objects at one time. and wait for reply messages after all the requests are sent.
        Similar to SyncClient.

    '''

    def before_publish(self, connection, request):
        super(AsyncClient, self).before_publish(connection, request)
        if request.get_timeout_time() > self.timeout_time:
            self.timeout_time = request.get_timeout_time()
        self.timeout_start = datetime.datetime.now()

    def after_publish(self, connection, request):
        pass

    def after_publish_all(self, connection):

        self.count_received = 0
        connection.basic_consume(self.get_reply_to())
        #print('basic_consume : ' + str(self.get_reply_to()))
        res = None
        while True:
            connection.process_data()
            received = connection.pop_received()

            if received is not None:

                isfound = self._bind_to_requests_by_correlation_id(received)
                if isfound:
                    self.count_received += 1

            if self.count_received == len(self.request_list):
                self._clean_rpq(connection)
                break

            if self._check_timeout():
                self._clean_rpq(connection)
                break

        connection.basic_cancel()

        super(AsyncClient, self).after_publish_all(connection)

    def _clean_rpq(self, connection):
        connection.queue_delete(self.get_reply_to())

    def _bind_to_requests_by_correlation_id(self, received):
        for request in self.request_list:
            #print ('_bind_to_requests_by_correlation_id %s  -  %s' %(received.get_correlation_id(),request.get_correlation_id()) )
            if received.get_correlation_id() == request.get_correlation_id():
                request.setrespond(received)
                return True

        return False


class NoreplyClient(BaseClient):

    '''Noreply class for Clients.

        Send requests at one time , and will not wait for responds.
    '''
    pass


if __name__ == '__main__':
    cp = build_connection_parameter('46.17.189.89', 5672, 4, 1, 'sjdev', 'cpos')
    conn_pool = ConnectionPool(cp, 1)

    num = 0
    tot = 2
    while True:

        req1 = Request({'num': num}, 'sjesb.trans', 'sj.trans', tot)
        num += 1
        req2 = Request({'num': num}, 'sjesb.trans', 'sj.trans', tot)
        num += 1
        req3 = Request({'num': num}, 'sjesb.trans', 'sj.trans', tot)
        num += 1
        req4 = Request({'num': num}, 'sjesb.trans', 'sj.trans', tot)
        num += 1
        req5 = Request({'num': num}, 'sjesb.trans', 'sj.trans', tot)
        num += 1
        req6 = Request({'num': num}, 'sjesb.trans', 'sj.trans', tot)
        num += 1

        client = AsyncClient(conn_pool)
        client.bind_requests([req1, req2, req3, req4, req5, req6])
        client.rpc()
        print('wait res')
        # continue
        if req1.getrespond():
            req1.getrespond().console_debug()
        if req2.getrespond():
            req2.getrespond().console_debug()
        if req3.getrespond():
            req3.getrespond().console_debug()
        if req4.getrespond():
            req4.getrespond().console_debug()
        if req5.getrespond():
            req5.getrespond().console_debug()
        if req6.getrespond():
            req6.getrespond().console_debug()
