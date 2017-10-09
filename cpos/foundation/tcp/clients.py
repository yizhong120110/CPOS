# -*- coding: utf-8 -*-
import socket
import select
from .framebuffer import *
from ..substrate.utils.logger import logger


class SelectClient(object):

    def __del__(self):
        if (self.mode == 'client'):
            self.shutdown()

    def __init__(self, host='127.0.0.1', port=3490, frame_decoder=None, peer=None):
        self.connected = False
        self.frame_decoder = frame_decoder

        self.outbound = FrameBuffer()
        self.inbound = FrameBuffer(self.frame_decoder)
        self.mode = 'client'
        if peer != None:
            self.sock = peer
            self.mode = 'peer'
            self.connected = True
            return

        #self.fb = FrameBuffer()
        self.port = int(port)
        self.host = host

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            self.sock.connect((self.host, self.port))
            self.connected = True
        except socket.error as e:
            logger.ods('Could not connect to tcp server @%d' % self.port, lv='dev', cat='foundation.tcp')
            raise RuntimeError('Could not connect to tcp server @%s' % str( (self.host, self.port)))

    def pop_inbound(self):
        self.do_select_comm()
        return self.inbound.pop_frame()
        #raise RuntimeError('[pop_inbound] has to be implemented at derived class.')

    def pop_inbound_without_comm(self):
        return self.inbound.pop_frame()

    # def pop_outbound (self):
    #    if self.outbound.get_buffer_length() == 0:
    #        return None
    #    return self.outbound.pop_buffer(0)

    def push_outbound(self, frame):
        self.outbound.push_frame(frame)
        self.do_select_comm()

    def push_outbound_without_comm(self, frame):
        self.outbound.push_frame(frame)

    def shutdown(self):
        if self.connected == False:
            return
        self.connected = False
        try:
            self.sock.close()
        except Exception as e:
            logger.ods((' ! ') + str(e), lv='dev', cat='foundation.tcp')

    def do_select_comm(self):
        try:
            inputready, outputready, exceptrdy = select.select([self.sock], [ ], [ ], 0.01)
            self.sock.send(self.outbound.get_buffer())
            self.outbound.clear_buffer()
            # only one socket descripter has been selected.
            for s in inputready:
                if s == self.sock:
                    buf = self.sock.recv(10240)
                    if not buf:
                        logger.ods('Socket is shutting down.', lv='dev', cat='foundation.tcp')
                        self.shutdown()
                        break
                    else:
                        while len(buf) == 10240:
                            self.inbound.append_buffer(buf)
                            buf = self.sock.recv(10240)
                    self.inbound.append_buffer(buf)

        except BlockingIOError as err:
            logger.ods(err, lv='info', cat='foundation.tcp')
            return

        except:
            logger.oes("clients do_select_comm error", lv='error', cat='foundation.tcp')
            self.sock.close()
            self.connected = False
            raise RuntimeError('[do_select_comm] failed.')


if __name__ == '__main__':
    client = SelectClient(port=18755)
    while True:
        client.push_outbound('12345'.encode('utf-8'))
        # client.do_select_comm()
        in_frame = client.pop_inbound()
        while in_frame is not None:
            print(bytes([in_frame]).decode('utf-8'))
            in_frame = client.pop_inbound()
    client.shutdown()
    #client = None
