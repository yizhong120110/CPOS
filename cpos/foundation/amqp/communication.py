#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""
import socket
import sys
import select

import pickle
import struct
import math
import time


from ..substrate.utils.logger import logger
from .parameters import *
from .frame import *
from .spec import *
from .exceptions import *
from ..tcp.framebuffer import FrameBuffer
from ..tcp.clients import SelectClient


class AMQPClient(SelectClient):

    def __init__(self, connection_parameter):
        super(AMQPClient, self).__init__(connection_parameter.host, connection_parameter.port)
        self.inbound.set_decoder(amqp_decode_frame)
        self.outbound.set_decoder(amqp_decode_frame)
        self.cp = connection_parameter

        self.last_df = None

        #{id : {method:method , header: header , body:body} }
        self.channels = {}

        #{id : callback, }
        self.callbacks = {}

    def _get_body_frame_max_length(self):
        """Calculate the maximum amount of bytes that can be in a body frame.

        :rtype: int

        """
        return (self.cp.frame_max -
                spec.FRAME_HEADER_SIZE -
                spec.FRAME_END_SIZE)

    def bind_callback(self, channel_number, cb=None):
        self.callbacks[channel_number] = cb

    def unbind_callback(self, channel_number):
        self.callbacks.pop(channel_number, None)

    #############  EXCHANGE  ##################
    def exchange_declare(self, channel_number, ticket=0, exchange=None, type='direct', passive=False,
                         durable=False, auto_delete=False, internal=False, nowait=False, arguments={}):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[exchange_declare] failed, channel(%d) does not exists. ' % channel_number)

        self._send_method(channel_number,  Exchange.Declare(ticket=ticket, exchange=exchange, type=type, passive=passive, durable=durable, auto_delete=auto_delete,
                                                            internal=internal, nowait=nowait, arguments=arguments))
        return self._wait_method_responds(channel_number, ['Exchange.DeclareOk']) is not None

    def exchange_delete(self, channel_number, ticket=0, exchange=None, if_unused=False, nowait=False):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[exchange_delete] failed, channel(%d) does not exists. ' % channel_number)

        self._send_method(channel_number,  Exchange.Delete(ticket=ticket, exchange=exchange, if_unused=if_unused, nowait=nowait))
        return self._wait_method_responds(channel_number, ['Exchange.DeleteOk']) is not None

    #############  QUEUE  ##################
    def queue_declare(self, channel_number, ticket=0, queue='', passive=False, durable=False,
                      exclusive=False, auto_delete=False, nowait=False, arguments={}):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[queue_declare] failed, channel(%d) does not exists. ' % channel_number)

        self._send_method(channel_number,  Queue.Declare(ticket=ticket, queue=queue, passive=passive, durable=durable, exclusive=exclusive,
                                                         auto_delete=auto_delete, nowait=nowait, arguments=arguments))
        return self._wait_method_responds(channel_number, ['Queue.DeclareOk']) is not None

    def queue_delete(self, channel_number, ticket=0, queue='', if_unused=False, if_empty=False, nowait=False):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[queue_delete] failed, channel(%d) does not exists. ' % channel_number)

        self._send_method(channel_number,  Queue.Delete(ticket=ticket, queue=queue, if_unused=if_unused, if_empty=if_empty, nowait=nowait))
        return self._wait_method_responds(channel_number, ['Queue.DeleteOk']) is not None

    def queue_bind(self, channel_number, ticket=0, queue='', exchange=None, routing_key='', nowait=False, arguments={}):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[queue_bind] failed, channel(%d) does not exists. ' % channel_number)

        self._send_method(channel_number,  Queue.Bind(ticket=ticket, queue=queue, exchange=exchange,
                                                      routing_key=routing_key, nowait=nowait, arguments=arguments))
        return self._wait_method_responds(channel_number, ['Queue.BindOk']) is not None

    #############  BASIC  ##################

    def basic_qos(self, channel_number, prefetch_size=0, prefetch_count=0, global_=False):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[basic_qos] failed, channel(%d) does not exists. ' % channel_number)

        self._send_method(channel_number,  Basic.Qos(prefetch_size=prefetch_size, prefetch_count=prefetch_count, global_=global_))
        return self._wait_method_responds(channel_number, ['Basic.QosOk']) is not None

    def basic_consume(self, channel_number, ticket=0, queue='', consumer_tag='',
                      no_local=False, no_ack=False, exclusive=False, nowait=False, arguments={}):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[basic_consume] failed, channel(%d) does not exists. ' % channel_number)

        self._send_method(channel_number,  Basic.Consume(ticket=ticket, queue=queue, consumer_tag=consumer_tag,
                                                         no_local=no_local, no_ack=no_ack, exclusive=exclusive, nowait=nowait, arguments=arguments))
        res = self._wait_method_responds(channel_number, ['Basic.ConsumeOk'])
        if res is not None:
            return res.method.consumer_tag
        return ''

    def basic_cancel(self, channel_number, consumer_tag=None, nowait=False):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[basic_cancel] failed, channel(%d) does not exists. ' % channel_number)

        self._send_method(channel_number,  Basic.Cancel(consumer_tag=consumer_tag, nowait=nowait))
        return self._wait_method_responds(channel_number, ['Basic.CancelOk']) is not None

    def basic_ack(self, channel_number, delivery_tag=0, multiple=False):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[basic_ack] failed, channel(%d) does not exists. ' % channel_number)

        self._send_method(channel_number,  Basic.Ack(delivery_tag=delivery_tag, multiple=multiple))

    def basic_publish(self, channel_number, exchange, routing_key, body,
                      properties=None, mandatory=False, immediate=False):

        if not self.is_channel_open(channel_number):
            if not self.channel_open(channel_number):
                raise AMQPError('[basic_publish] failed, channel(%d) does not exists. ' % channel_number)

        if isinstance(body, str):
            body = body.encode('utf-8')
        if isinstance(body, bytes) or isinstance(body, bytearray):
            # No need to log it.
            pass
        properties = properties or spec.BasicProperties()

        self._send_method(channel_number,  Basic.Publish(exchange=exchange, routing_key=routing_key,
                                                         mandatory=mandatory, immediate=immediate))

        length = len(body)
        self._send_header(Header(channel_number, length, properties))

        if body:
            chunks = int(math.ceil(float(length) / self._get_body_frame_max_length()))
            for chunk in range(0, chunks):
                start = chunk * self._get_body_frame_max_length()
                end = start + self._get_body_frame_max_length()
                if end > length:
                    end = length
                self._send_body(Body(channel_number, body[start:end]))

        self.process_data()

    #############################################################################
    # Not Implement yet.

    #############################################################################
    # def channel_flow (self,channel_number,active = 1):
    #    '''RabbitMQ havent implemented this feature.
    #    '''
    #    if not self.is_channel_open(channel_number):
    #        return False
    #
    #    self._send_method(channel_number,  Channel.Flow(active) )
    #    return self._wait_method_responds(channel_number,['Channel.FlowOk']) is not None

    # def exchange_bind (self,channel_number,ticket=0, destination=None, source=None, routing_key='', nowait=False, arguments={}):
    #    ''' RabbitMQ supports exchange to exchange binding .  AMQP doesnt have this spec.
    #    '''
    #    if not self.is_channel_open(channel_number):
    #        return False

    #    self._send_method(channel_number,  Exchange.Bind(ticket=ticket, destination=destination,
    #                        source=source, routing_key=routing_key, nowait=nowait, arguments=arguments) )
    #    return self._wait_method_responds(channel_number,['Exchange.BindOk']) is not None

    ############################################################################

    def is_channel_open(self, channel_number):
        # return true if the channel is already open.
        if self.channels.get(channel_number) is not None:
            return True
        return False

    def channel_open(self, channel_number):
        if self.is_channel_open(channel_number):
            return True

        self._send_method(channel_number,  Channel.Open())
        if self._wait_method_responds(channel_number, ['Channel.OpenOk']) is not None:
            self.channels[channel_number] = {}
            return True
        else:
            return False

    def channel_close(self, channel_number, reply_code=0, reply_text='', class_id=0, method_id=0):
        self._send_method(channel_number,  Channel.Close(reply_code, reply_text, class_id, method_id))
        if self._wait_method_responds(channel_number, ['Channel.CloseOk']) is not None:
            self.channels.pop(channel_number, None)
            return True
        else:
            return False

    def connection_open(self):
        ph = ProtocolHeader()
        self.push_outbound(ph)

        while self.connected:
            self.process_data()
            if self.last_df is None:
                continue
            if self.last_df.frame_type == spec.FRAME_METHOD:
                if self.last_df.method.NAME == 'Connection.OpenOk':
                    return True
        return False

    def connection_close(self, reply_code=0, reply_text='', class_id=0, method_id=0):

        so = Connection.Close(reply_code, reply_text, class_id, method_id)
        ff = Method(0, so)
        self.push_outbound(ff)

        while self.connected:
            self.process_data()
            if self.last_df is None:
                continue
            if self.last_df.frame_type == spec.FRAME_METHOD:
                if self.last_df.method.NAME == 'Connection.CloseOk':
                    self.shutdown()
                    return True
        return False

    def _send_method(self, channel_number, m):
        try:
            ff = Method(channel_number, m)
            logger.ods('_send_method (%d - %s) ' % (channel_number, str(ff)), lv='dev', cat='foundation.amqp')
            self.push_outbound(ff)
            self.do_select_comm()
        except Exception as err:
            raise AMQPError('[_send_method] failed. ')

    def _send_header(self, h):
        try:
            logger.ods('_send_header (%s) ' % (str(h)), lv='dev', cat='foundation.amqp')
            self.push_outbound_without_comm(h)
            # self.do_select_comm()
        except Exception as err:
            raise AMQPError('[_send_header] failed. ')

    def _send_body(self, b):
        try:
            logger.ods('_send_body (%s) ' % (str(b)), lv='dev', cat='foundation.amqp')
            self.push_outbound_without_comm(b)
            # self.do_select_comm()
        except Exception as err:
            raise AMQPError('[_send_body] failed. ')

    def _wait_method_responds(self, channel_number, resp_names):
        logger.ods('_wait_method_responds (%d - %s) ' % (channel_number, resp_names), lv='dev', cat='foundation.amqp')
        while True:
            df = self.pop_inbound()
            if df is None:
                continue

            self.last_df = df
            if self.last_df.frame_type == spec.FRAME_HEARTBEAT:
                self.push_outbound(self.last_df)

            if self.last_df.frame_type == spec.FRAME_BODY:
                self._on_body(self.last_df)

            if self.last_df.frame_type == spec.FRAME_HEADER:
                self._on_header(self.last_df)

            if self.last_df.frame_type == spec.FRAME_METHOD:
                if self._on_method(self.last_df) == False:
                    if self.last_df.method.reply_code != 0:
                        logger.ods('AMQP connection/channel closed with exception.'
                                   '\n%s' % (str(self.last_df)),
                                   lv='warning', cat='foundation.amqp')
                        return self.last_df

                if resp_names.count(self.last_df.method.NAME) > 0:
                    return self.last_df

        return None

    def _on_method(self, df):
        #ods('received method : ' + df.method.NAME)

        if df.method.NAME == 'Connection.Start':
            res = self.cp.credentials.response_for(df.method)
            so = Connection.StartOk(CLIENT_PROPERTIES, res[0], res[1], 'en_US')
            ff = Method(0, so)
            self.push_outbound(ff)

        if df.method.NAME == 'Connection.Tune':
            so = Connection.TuneOk(self.cp.channel_max, FRAME_MAX_SIZE, self.cp.heartbeat_interval)
            ff = Method(0, so)
            self.push_outbound(ff)

            so = Connection.Open('/', '', True)
            ff = Method(0, so)
            self.push_outbound(ff)

        if df.method.NAME == 'Connection.Close':
            so = Connection.CloseOk()
            ff = Method(0, so)
            self.push_outbound(ff)
            self.do_select_comm()
            self.channels.clear()
            self.shutdown()
            return False

        if df.method.NAME == 'Channel.Close':
            so = Channel.CloseOk()
            ff = Method(df.channel_number, so)
            self.push_outbound(ff)
            self.do_select_comm()
            self.channels.pop(df.channel_number, None)
            return False

        if df.method.NAME == 'Basic.Deliver':
            '''
            received method : Basic.Deliver
            _on_method > <METHOD(['channel_number=1', 'frame_type=1', "method=<Basic.Deliver(['consumer_tag=amq.ctag-wnWh30CMEETticppIy6yQg', 'delivery_
            tag=1', 'exchange=', 'redelivered=True', 'routing_key=123456'])>"])>
            _on_header > <Header(['body_size=40', 'channel_number=1', 'frame_type=2', 'properties=<BasicProperties([\'delivery_mode=1\', "headers={b\'he
            ader\': \'AAAAHeader\'}", \'reply_to=BBBBREPLY\'])>'])>
            _on_body > <Body(['channel_number=1', "fragment=b'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'", 'frame_type=3'])>
            '''
            self.channels[df.channel_number] = {}
            self.channels[df.channel_number]['method'] = df.method
        return True

    def _on_header(self, df):
        self.channels[df.channel_number]['header'] = df
        self.channels[df.channel_number]['body'] = bytearray()

    def _on_body(self, df):
        self.channels[df.channel_number]['body'] += df.fragment

        if len(self.channels[df.channel_number]['body']) == self.channels[df.channel_number]['header'].body_size:
            cb = self.callbacks.get(df.channel_number, None)
            if cb is not None:
                cb(df.channel_number, self.channels[df.channel_number]['method'],
                    self.channels[df.channel_number]['header'],
                    self.channels[df.channel_number]['body'])

    def process_data(self):

        self.do_select_comm()

        df = self.pop_inbound()
        self.last_df = df
        while df is not None:
            self.last_df = df

            #ods('Decoded frame : ' + str(df))

            # heart beat
            if df.frame_type == spec.FRAME_HEARTBEAT:
                self.push_outbound(df)

            if df.frame_type == spec.FRAME_BODY:
                self._on_body(df)

            if df.frame_type == spec.FRAME_HEADER:
                self._on_header(df)

            if df.frame_type == spec.FRAME_METHOD:
                self._on_method(df)
            df = self.pop_inbound_without_comm()
        return True

    def data_loop(self):
        while self.connected:
            self.process_data()


#################################################################################

cp = None
ac = None

mc = 0


def on_message(channel_number, method, header, body):
    global mc
    print('on_message ###########################################')
    print( str(method))
    print( str(header))
    print( str(body))
    ac.basic_ack(channel_number, method.delivery_tag)
    mc += 1
    print('received messages : ' + str(mc))


def test2():
    global cp
    #cp = build_connection_parameter('46.17.189.236',5677,0,0,'sjdev','sjdev')
    cp = build_connection_parameter('127.0.0.1', 5672, 0, 0, 'sjdev', 'cpos')
    global ac
    ac = AMQPClient(cp)

    ac.connection_open()
    ac.channel_open(1)
    ac.bind_callback(1, on_message)
    # ac.ctl_flow(1,1)
    # ac.ctl_flow(1,0)

    ac.exchange_declare(1, exchange='test_exchange11', type='topic', durable=False, auto_delete=True)

    ac.queue_declare(1, queue='123456')
    ac.queue_bind(1, queue='123456', exchange='test_exchange11', routing_key='a.b')
    # ac.queue_delete(1,queue='123456')

    # ac.exchange_delete(1,exchange='test_exchange11')
    ac.basic_qos(1, prefetch_count=1)
    ac.basic_consume(1, queue='123456')

    a = 0
    while True:

        ac.basic_publish(1, exchange='test_exchange11',
                         routing_key='a.b',
                         properties=BasicProperties(
                             delivery_mode=1,
                             reply_to='rrr',
                             correlation_id='111111111111',
                         ),
                         body=(str( 'This is body')).encode('utf-8')
                         )
        a += 1
    # ac.channel_close(1)
    # ac.connection_close()
        ac.process_data()

    ac.data_loop()


def test1():

    cp = build_connection_parameter('localhost', 5672, 0, 0, 'sjdev', 'cpos')

    client = SocketClient(cp.host, cp.port)
    p = ProtocolHeader()
    client.push_outbound(p)

    while client.connected:
        client.do_select_comm()
        rcv = client.pop_inbound()
        if rcv is not None:
            dl, df = decode_frame(rcv)
            # heart beat
            if isinstance(df, Heartbeat):
                client.push_outbound(df)
                continue

            if df.method.NAME == 'Connection.Start':
                res = cp.credentials.response_for(df.method)
                so = Connection.StartOk(CLIENT_PROPERTIES, res[0], res[1], 'en_US')
                ff = Method(0, so)
                self.push_outbound(ff)

            if df.method.NAME == 'Connection.Tune':
                so = Connection.TuneOk(cp.channel_max, FRAME_MAX_SIZE, 0)
                ff = Method(0, so)
                self.push_outbound(ff)

                so = Connection.Open('/', '', True)
                ff = Method(0, so)
                self.push_outbound(ff)

            if df.method.NAME == 'Connection.Close':
                so = Connection.CloseOk()
                ff = Method(0, so)
                self.push_outbound(ff)


if __name__ == "__main__":
    test2()
