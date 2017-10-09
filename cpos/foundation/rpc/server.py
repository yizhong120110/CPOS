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
from ..substrate.interfaces import *
from ..substrate.utils.logger import logger


class BaseServer(Monitored):

    '''RPC 服务基类.

    '''

    def __init__(self, connection_pool, queue_list):
        self.queue_list = queue_list
        self.connection_pool = connection_pool
        self.keep_running = True

    def _consume_queues(self, connection):
        connection.basic_cancel()
        for q in self.queue_list:
            connection.basic_consume(q)

    def on_ticks(self):
        return True

    def on_start(self, connection):
        pass

    def after_callback(self, connection, received, cb_result):
        pass

    def run(self, cb):
        try:
            connection = self.connection_pool.get_free_connection()
            self.on_start(connection)
            self._consume_queues(connection)
            result = None
            while True:
                connection.process_data()
                received = connection.pop_received()
                while received is not None:
                    result, kr = cb(received)
                    self.after_callback(connection, received, result)
                    if kr == False:
                        self.keep_running = False

                    received = connection.pop_received()

                kr = self.on_ticks()
                if kr == False:
                    self.keep_running = False

                if self.keep_running == False:
                    break

        except Exception as err:
            logger.oes("Server has encountered an error!", lv='error', cat='esb.rpc')
            connection.makesure_alive()
        finally:
            self.connection_pool.recycle_connection(connection)


class TimeLimitedServer(BaseServer):

    '''RPC 服务扩展类, 支持timeout.

    '''

    def __init__(self, connection_pool, queue_list):
        super(TimeLimitedServer, self).__init__(connection_pool, queue_list)

    def run(self, cb, timeout_time=-1):
        self.timeout_time = timeout_time
        super(TimeLimitedServer, self).run(cb)

    def on_start(self, connection):
        super(TimeLimitedServer, self).on_start(connection)
        self.timeout_start = datetime.datetime.now()

    def on_ticks(self):
        super(TimeLimitedServer, self).on_ticks()
        if self.timeout_time == -1:
            return True

        dt = datetime.datetime.now() - self.timeout_start
        return dt.total_seconds() < self.timeout_time


# support to send messages back
class RPCServer(TimeLimitedServer):

    '''RPC 服务扩展类, 支持timeout及返回消息.

    '''

    def __init__(self, connection_pool, queue_list):
        super(RPCServer, self).__init__(connection_pool, queue_list)

    def after_callback(self, connection, received, cb_result):
        self._send_result_back(connection, received, cb_result)
        super(RPCServer, self).after_callback(connection, received, cb_result)
        return True

    def _send_result_back(self, connection, received=None, result=None):
        # print('_send_result_back')
        if result == None or received == None:
            return
        if received.get_reply_to() == None:
            return
        reply = Reply(result, received)
        connection.basic_publish(reply)


# preconfigured server
# eg.:
'''
wqs_transaction =   {   'exchange'  :   'sjesb.trans' , 'queue' : 'q.trans' ,
                        'binding_key' : 'sj.trans' , 'queue_durable':True }

[wqs_transaction,]
'''


class PreConfServer(RPCServer):

    '''RPC 服务扩展类, 支持timeout及返回消息, 并且支持预定义的服务配置.

        服务配置必须是如下格式字典的列表:

        wqs_transaction =   {   'exchange'  :   'sjesb.trans' , 'queue' : 'q.trans' ,
                        'binding_key' : 'sj.trans' , 'queue_durable':True }

    '''

    def __init__(self, connection_pool, mqs_conf_list):
        self.mqs_conf_list = mqs_conf_list
        queue_list = []
        for mqs in mqs_conf_list:
            queue_list.append(mqs['queue'])

        super(PreConfServer, self).__init__(connection_pool, queue_list)

    def run(self, cb, timeout_time=-1, mqs_prep=True):
        self.mqs_prep = mqs_prep
        super(PreConfServer, self).run(cb, timeout_time)

    def on_start(self, connection):
        super(PreConfServer, self).on_start(connection)
        if self.mqs_prep:
            self._mqs_prep(connection)

    def _mqs_prep(self, connection):
        for conf in self.mqs_conf_list:
            connection.exchange_declare(conf['exchange'], 'topic', conf['queue_durable'])
            connection.queue_declare(conf['queue'], conf['queue_durable'])
            connection.queue_bind(conf['exchange'], conf['queue'], conf['binding_key'])


#########################################################################################

num = 1


def test_server(received):
    print( '-------------------------------------------')
    global num
    print( 'test_server received : ' + str(received._data))
    print('\n')
    map_res = {'key1': 'this is key1', 'key2': str(num)}
    print('return : ' + str(map_res))
    num += 1
    print('-------------------------------------------')
    return map_res, True

if __name__ == '__main__':
    print("server start")

    wqs_transaction = {   'exchange':   'sjesb.trans', 'queue': 'q.trans',
                          'binding_key': 'sj.trans', 'queue_durable': True}

    cp = build_connection_parameter('46.17.189.89', 5672, 4, 1, 'sjdev', 'cpos')
    conn_pool = ConnectionPool(cp, 1)
    server = PreConfServer(conn_pool, [wqs_transaction])

    while server.keep_running:
        server.run(test_server)
    print('END')
