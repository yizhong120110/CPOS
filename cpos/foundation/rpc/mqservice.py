#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This is a module to provide the basic toolkit to access RabbitMQ service.
"""

__author__ = 'Percy'
__version__ = '1.0'
__create_data__ = '2015/1/29'

import uuid
import datetime
import time
import threading
import json
from .exceptions import *
from .messages import *
from ..substrate.interfaces import *
from ..amqp.parameters import *
from ..amqp.communication import *
from ..amqp.exceptions import *
from ..substrate.utils.logger import logger


class Connection(Monitored):

    """Connection wraps operators for RabbitMQ service.

        Connections are not thread-safe, make sure no shared connection between threads.
    Although AMQP allows multiple channels to be declared on a single connection
    and each of them is able to perform 'basic_consume' respectively, this implementation still keep single channel on every connection.
    Reasons:
        1. Robust and stable.  In this design, a single connection dropped by exceptions will not affact the whole system.
        2. Connections to the RabbitMQ server are limited on number. So, the system resource consumption of one-connection-one-channel mode is acceptable.
    """

    __number = 0

    def __init__(self, connection_parameter):
        """Initialize a connection object with given paramters.

            The paramter can be created by calling build_connection_parameter().
        """

        super(Connection, self).__init__()
        self.connection = None
        self.connection_parameter = connection_parameter
        self._isfree = threading.Event()
        self._isfree.clear()
        self.setname('#'.join([str(connection_parameter.host), str(connection_parameter.port), str(self.__class__.__number)]))
        self.__class__.__number += 1
        self.reply_to = uuid.uuid4().hex
        self.received_list = []
        self.received_guard = threading.RLock()

        self.consumer_tags = []

    def makesure_alive(self, force_reopen=False):
        """Make sure the connection is initialized and alive.

            Call this method after a connection object initialized with connection_parameter.

        Args:
            force_reopen - [bool] If set to True, the opened connection will be shutdown and re-opened.
        """
        if self.connection == None:
            while self._open() != True and self.connection_parameter.connection_attempts > 0:
                time.sleep(self.connection_parameter.retry_delay)
                pass

        if self.connection == None:
            return None

        if self.connection.connected == False:
            while self._open() != True and self.connection_parameter.connection_attempts > 0:
                pass
            return self.getname()

        # opening , but being forced to refresh
        if self.connection.connected and force_reopen == True:
            self.connection.shutdown()
            while self._open() != True and self.connection_parameter.connection_attempts > 0:
                pass

        return self.getname()

    def _open(self):
        """Open connection with the parameter.

            The parameter should be passed in while initialize the connection object.
        Don't call this manually, should call makesure_alive method instead.
        """
        try:
            self._isfree.set()
            self.connection = AMQPClient(self.connection_parameter)
            self.connection.connection_open()
            self.connection.channel_open(1)
            self.connection.basic_qos(channel_number=1, prefetch_count=10)
            return True

        except Exception as err:
            logger.oes("Exception occured while opening a RMQ connection.", lv='error', cat='esb.rpc')
            return False

    def shutdown(self):
        """Close the connection.

        """

        try:
            for t in self.consumer_tags:
                self.connection.basic_cancel(1, t)
            self.consumer_tags.clear()
            self.connection.shutdown()

        except Exception as err:
            logger.oes("Exception occured while closing a RMQ connection.Ignored.", lv='warning', cat='esb.rpc')
        finally:
            self._isfree.clear()

    def setbusy(self):
        """Set the connection to busy mode, so other threads won't use it.

        """
        self._isfree.clear()

    def setfree(self):
        """Set the connection to free mode, so other threads are able to use it.

        Consuming will be stopped if the consuming is going.
        """

        for t in self.consumer_tags:
            self.connection.basic_cancel(1, t)
        self.consumer_tags.clear()
        self._isfree.set()

    def isfree(self):
        """Test if the connection is free.

        """
        return self._isfree.is_set()

    def exchange_declare(self, exchange, type, durable):
        """Declare an exchange on the RabbitMQ server.

        Args:
            exchange - [str] Name of the exchange. (Refer to AMQP SPEC)
            type - [str] Type of the exchange. Options : direct,topic,fanout ... (Refer to AMQP SPEC)
            durable - [bool] Indicate if the exchange is durable. (Refer to AMQP SPEC)
        """
        try:
            self.connection.exchange_declare(1, exchange=exchange, type=type, durable=durable)
        except AMQPError as err:
            logger.oes("", lv='error', cat='esb.rpc')
            raise SJRPCExceptionBadCall('Exchange declaring is failed, connection name : [%s] .' % (self.getname()))

    # def reply_to_declare (self):
    #    self.queue_declare( self.reply_to, False, False)
    #    return self.reply_to

    def queue_declare(self, queue, durable=False, exclusive=False):
        """Declare a queue on the RabbitMQ server.

        Args:
            queue - [str] Name of the queue. (Refer to AMQP SPEC)
            durable - [str] Indicate if the queue is durable. (Refer to AMQP SPEC)
            exclusive - [str] Indicate if the queue is exclusive. (Refer to AMQP SPEC)
        """
        try:
            self.connection.queue_declare(1, queue=queue, durable=durable, exclusive=exclusive)
        except AMQPError as err:
            logger.oes("", lv='error', cat='esb.rpc')
            raise SJRPCExceptionBadCall('Queue declaring is failed, connection name : [%s] .' % (self.getname()))

    def queue_delete(self, queue):
        """Delete a queue on the RabbitMQ server.

        Args:
            queue - [str] Name of the queue. (Refer to AMQP SPEC)
        """
        try:
            for t in self.consumer_tags:
                self.connection.basic_cancel(1, t)

            self.consumer_tags.clear()
            self.connection.queue_delete(1, queue=queue, nowait=False)

        except AMQPError as err:
            logger.oes("", lv='error', cat='esb.rpc')
            raise SJRPCExceptionBadCall('Queue deleting is failed, connection name : [%s] .' % (self.getname()))

    def queue_bind(self, exchange, queue, binding_key):
        """Bind the queue and exchange together with binding_key on the RabbitMQ server.

        NOTE: AMQP API Uses routing_key as binding_key.

        Args:
            exchange - [str] Name of the exchange. (Refer to AMQP SPEC)
            queue - [str] Name of the queue. (Refer to AMQP SPEC)
            binding_key - [str] Binding key. (Refer to AMQP SPEC)
        """
        try:
            self.connection.queue_bind(1, exchange=exchange, queue=queue, routing_key=binding_key)
        except AMQPError as err:
            logger.oes("", lv='error', cat='esb.rpc')
            raise SJRPCExceptionBadCall('Queue declaring is failed, connection name : [%s] .' % (self.getname()))

    # def _onrequest (self,ch, method, props, body):
    def _onrequest(self, channel_number, method, header, body):
        #print ('_onrequest')
        """Called by inner loop while a message received from listened queues.

            Package the inbound message into Received object, and put it into the inbound buffer.
        """
        try:
            self.received_guard.acquire()
            self.received_list.append( Received(body, method.exchange, method.routing_key, header.properties.reply_to, header.properties.correlation_id))
            #print ('basic_ack ' + str(method.delivery_tag))
            self.connection.basic_ack(channel_number, method.delivery_tag)
        finally:
            self.received_guard.release()

    def pop_received(self):
        """Pop messages out that received from the RabbitMQ server.

            Should call this method everytime after calling process_data().
        Connection objects hold a buffer for storing the inbound messages, this method returns a single message to caller
        in FIFO approach.

        Returns:
            A Received object that popped from the inbound buffer.
            Return None if the buffer is empty.
        """
        try:
            self.received_guard.acquire()
            if len(self.received_list) == 0:
                return None
            else:
                return self.received_list.pop(0)
        finally:
            self.received_guard.release()

    def basic_cancel(self):
        for t in self.consumer_tags:
            self.connection.basic_cancel(1, t)

        self.consumer_tags.clear()

    def basic_consume(self, queue):
        """Consume messages from the queue on RabbitMQ server.

            Can be called multiple times to consume from different queues at one channel.

        Args:
            queue - [str] Name of the queue.
        """
        try:
            self.connection.bind_callback(1, self._onrequest)
            self.consumer_tags.append( self.connection.basic_consume(1, queue=queue, no_ack=False))
        except AMQPError as err:
            logger.oes("", lv='error', cat='esb.rpc')
            raise SJRPCExceptionBadCall('Message consuming is failed, connection name : [%s] .' % (self.getname()))

    def basic_publish(self, message, reply_to=None):
        """Publish messages to RabbitMQ server.

        Args:
            message - [str] A Request object.
            reply_to - [str] Name of the replay_to queue.  None represents no replay message need to be sent back.
        """
        try:

            self.connection.basic_publish(1, exchange=message.getexchange(),
                                          routing_key=message.get_routing_key(),
                                          properties=BasicProperties(
                reply_to=reply_to,
                correlation_id=message.get_correlation_id(),
            ),
                body=message.get_content_raw()
            )
        except AMQPError as err:
            logger.oes("", lv='error', cat='esb.rpc')
            raise SJRPCExceptionBadCall('Message publishing is failed, connection name : [%s] .' % (self.getname()))

    def process_data(self):
        """Will make sure that data events are processed. Caller can block on this method.

        """

        try:
            # rint "calling connection:process_data()"
            self.connection.process_data()
        except Exception as err:
            logger.oes("", lv='error', cat='esb.rpc')
            raise SJRPCExceptionRtError('Process_data failed(unknow reason), connection name : [%s] .' % (self.getname()))


class ConnectionPool(Monitored):

    """A ConnectionPool that provides pooling mechanism and thread-saft guarantee for connections .

        Callers in different threads should only be allowed to get connections from ConnectionPool.
    """
    __number = 0

    def __init__(self, connection_parameter, pool_init_size=1):
        """Initialize a ConnectionPool object.

        """
        super(ConnectionPool, self).__init__()

        self._connections = []
        self._pguard = threading.RLock()
        #self.pool_size = pool_init_size
        self.connection_parameter = connection_parameter
        self.__class__.__number += 1
        self.spawn_connections(pool_init_size)

        # Indicates how many times [get_free_connection]
        # has been called since last time the pool shrank.
        self.query_counter = 0

    def spawn_connections(self, pool_size):
        """Spawn connections up to specified numbers.

        """
        try:
            self._pguard.acquire()
            if len(self._connections) >= pool_size:
                # poolsize is already exceeded the new size . no need to spawn any new connection.

                logger.ods('poolsize is already exceeded(or equal to) the new size .'
                           'no need to spawn any new connection.',
                           lv='warning', cat='esb.rpc')
                return

            # update name (pool_size)
            ori_pool_size = len(self._connections)
            self.setname('#'.join([str(self.connection_parameter.host),
                                   str(self.connection_parameter.port), str(pool_size),
                                   str(self.__class__.__number)]))
            for i in range(ori_pool_size, pool_size):
                conn = Connection(self.connection_parameter)
                conn.makesure_alive()
                self._connections.append(conn)
                self.query_counter = 0
        finally:
            self._pguard.release()

    def get_free_connection_count(self):
        count = 0
        with self._pguard:
            for c in self._connections:
                if c.isfree():
                    count += 1
        return count

    def shrink_pool(self):
        # shrink the pool. clean up only one free connection every time.
        with self._pguard:
            for c in self._connections:
                if c.isfree():
                    c.shutdown()
                    self._connections.remove(c)
                    logger.ods('ConnectionPool shrunk.',
                               lv='info', cat='esb.rpc')
                    break

    def get_free_connection(self):
        """Get a free connection.

        """
        try:
            self._pguard.acquire()

            fc = self.get_free_connection_count()
            if fc < 1:
                new_size = int(len(self._connections) * 1.4) + 1
                logger.ods('Enlarge connectionPool.(%d -> %d)'
                           % (len(self._connections),
                               int(len(self._connections) * 1.4) + 1),
                           lv='info', cat='esb.rpc')
                self.spawn_connections(new_size)

            for c in self._connections:
                if c.isfree():
                    c.makesure_alive()
                    c.setbusy()
                    return c
            return None  # should never happens.

        finally:
            self._pguard.release()

    def recycle_connection(self, connection):
        """Recycle a connection

            If the connection is still consuming, it will be stoped by calling the setfree() on it.

        """
        try:
            self._pguard.acquire()
            connection.setfree()

            fc = self.get_free_connection_count()
            ratio_fc = fc/1.0/len(self._connections)

            # algorithm: frequency = 10 / ratio_fc + 10
            if ratio_fc != 0.0:
                if self.query_counter >= (10 / ratio_fc + 10):
                    if fc > 1:
                        self.shrink_pool()
                        self.query_counter = 0
                else:
                    self.query_counter += 1
        finally:
            self._pguard.release()

    def clear(self):
        """Shutdown all the connections that holding by the ConnectionPool, and clean up the pool.

            Warning: Callers have to make sure all the connections are stop working before call this.

        Returns:
            True if succeessed.
            False if there are connections still busy, leave the ConnectionPool object intact.

        """
        try:
            self._pguard.acquire()
            allfree = True
            for c in self._connections:
                allfree = c.isfree()
                if IsAllFree == False:
                    break

            if allfree == True:
                for c in self._connections:
                    c.shutdown()
                self._connection.clear()

                return True
            return False
        finally:
            self._pguard.release()


if __name__ == '__main__':
    print("start")
    logger.level('info')
    logger.ods('sssss', lv='error', cat='esb.rpc')
    '''
    rd = Respond('method.exchange','method.routing_key','props.reply_to','props.correlation_id','body')
    rd.console_debug()
    '''

    cp = build_connection_parameter('localhost', 5672, 4, 1, 'sjdev', 'cpos')
    conn_pool = ConnectionPool(cp, 20)
    res = None
    conn = conn_pool.get_free_connection()
    conn.exchange_declare('test_exchange', 'topic', True)
    conn.queue_declare('test_q', True)
    conn.queue_bind('test_exchange', 'test_q', 'test.bk')

    req = Request({'a-key': 'a-value'}, 'test_exchange', 'test.bk')
    conn.basic_consume('test_q')
    while True:
        # conn_tmp = conn_pool.get_free_connection() # test , dont recycle.

        #req = Request(bytearray([1,2,3,4,5]),'test_exchange','test.bk')
        #print (req)
        conn.basic_publish(req)

        rev = conn.pop_received()
        #print (str(rev))
        if rev is not None:
            # rev.console_debug()
            print(rev.getcontent())
        conn.basic_publish(req)
        conn.process_data()
        # conn_pool.recycle_connection(conn)
