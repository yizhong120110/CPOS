# -*- coding: utf-8 -*-
import socket
import select
import queue
import threading
from .framebuffer import *
from ..substrate import interfaces
from ..substrate.utils.logger import logger


class DummyLocker(object):

    def acquire(self):
        pass

    def release(self):
        pass


class SelectServer(interfaces.Named):
    NAME = 'SelectServer'

    def __del__(self):
        self.shutdown()

    def __init__(self, host='127.0.0.1', port=18755, frame_decoder=None):
        interfaces.Named.__init__(self)

        self.frame_decoder = frame_decoder
        self.s_lock = DummyLocker()

        self.port = int(port)
        self.host = host
        self.server_address = (host, port)

        self.to_close_socks = []

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setblocking(False)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(self.server_address)
            self.server.listen(0)

            # Collection of peers , every connection will be added to the inbound dic.
            self.inbound = {}
            self.outbound = {}

        except socket.error as e:
            logger.oes('Could not listen on port @%d' % self.port, lv='error', cat='foundation.tcp')
            raise RuntimeError('Could not listen on port @%d' % self.port)

    def _get_inputs(self):
        inputs = [] if self.server == None else [self.server]
        for peer in self.inbound:
            inputs.append(peer)
        return inputs

    def _get_outputs(self):
        outputs = []
        for peer in self.outbound:
            outputs.append(peer)
        return outputs

    def pop_inbound_nocomm(self):
        try:
            self.s_lock.acquire()
            for peer in self.inbound:
                df = self.inbound[peer].pop_frame()
                if df is not None:
                    return {'peer': peer, 'frame': df}

            return None
        finally:
            self.s_lock.release()

    def pop_inbound_clear(self):
        try:
            self.s_lock.acquire()
            self.do_select_comm()
            peer = None
            for peer in self.inbound:
                df = self.inbound[peer].pop_frame()
                if df is not None:
                    del ( self.inbound[peer])
                    return {'peer': peer, 'frame': df}

            return None
        finally:
            self.s_lock.release()

    def pop_inbound(self):
        try:
            self.s_lock.acquire()
            self.do_select_comm()
            for peer in self.inbound:
                df = self.inbound[peer].pop_frame()
                if df is not None:
                    return {'peer': peer, 'frame': df}

            return None
        finally:
            self.s_lock.release()
        #raise RuntimeError('[pop_inbound] has to be implemented at derived class.')

    def push_outbound_nocomm(self, peer, frame):
        try:
            self.s_lock.acquire()
            # connection has been lost , no need to send. return a false
            if self.inbound.get(peer) == None:
                return False

            if self.outbound.get(peer) == None:
                self.outbound[peer] = FrameBuffer()

            self.outbound[peer].push_frame(frame)
        finally:
            self.s_lock.release()

    def push_outbound(self, peer, frame):
        try:
            self.s_lock.acquire()
            # connection has been lost , no need to send. return a false
            if self.inbound.get(peer) == None:
                return False

            if self.outbound.get(peer) == None:
                self.outbound[peer] = FrameBuffer()

            self.outbound[peer].push_frame(frame)
            self.do_select_comm()
        finally:
            self.s_lock.release()

    def clear_outbound(self, peer):
        try:
            self.s_lock.acquire()
            # connection has been lost , no need to send. return a false
            if self.inbound.get(peer) == None:
                return False

            if self.outbound.get(peer) is not None:
                self.outbound[peer] = FrameBuffer()
            self.do_select_comm()
        finally:
            self.s_lock.release()

    def shutdown(self):
        try:
            self.s_lock.acquire()
            # self.server.shutdown(socket.SHUT_RDWR)
            if self.server != None:
                # self.server.close()
                self.server.shutdown(socket.SHUT_RDWR)
                self.server = None
        except Exception as e:
            print((' ! ') + str(e))
        finally:
            self.s_lock.release()

    def _clear_peer(self, peer_sock):
        #print ('clear peer : ' + str(peer_sock))
        if peer_sock in self.inbound:
            del(self.inbound[ peer_sock])

        if peer_sock in self.outbound:
            del(self.outbound[ peer_sock])

        if peer_sock in self.to_close_socks:
            self.to_close_socks.remove(peer_sock)

        try:

            # peer_sock.shutdown(socket.SHUT_RDWR)
            peer_sock.close()
        except Exception as e:
            logger.ods('Exception @ [_clear_peer]. Ignored.', lv='dev', cat='foundation.tcp')

    def close_peer(self, peer_sock):
        try:
            self.s_lock.acquire()
            if (not( peer_sock in self.to_close_socks)) and (peer_sock in self.inbound):
                self.to_close_socks.append(peer_sock)
        finally:
            self.s_lock.release()
        self.do_select_comm()

    def _chk_to_close(self, peer_sock):
        return peer_sock in self.to_close_socks

    def _proc_input(self, rlist):
        for sock in rlist:
            # if receiving a new connection
            if sock is self.server:
                try:
                    peer, client_address = sock.accept()
                    peer.setblocking(False)
                    self.inbound[ peer] = FrameBuffer(self.frame_decoder)
                except BlockingIOError as err:
                    logger.oes('BlockingIOError @ [_proc_input]1#', lv='dev', cat='foundation.tcp')
            else:
                try:
                    buf = sock.recv(10240)
                    # got a disconnecting msg.
                    if not buf:
                        self._clear_peer(sock)
                        break
                    else:
                        while len(buf) == 10240:
                            self.inbound[ sock].append_buffer(buf)
                            buf = sock.recv(10240)
                        self.inbound[ sock].append_buffer(buf)
                except BlockingIOError as err:
                    logger.ods('BlockingIOError @ [_proc_input]', lv='dev', cat='foundation.tcp')
                    return
                except Exception as err:
                    logger.oes("", lv='error', cat='foundation.tcp')
                    self._clear_peer(sock)

    def _proc_output(self, wlist):
        for sock in wlist:
            try:

                to_send = self.outbound[ sock].get_buffer()
                self.outbound[ sock].clear_buffer()
                if len(to_send) == 0:
                    pass

                else:
                    logger.ods("sending " + str(to_send) + " to " + str(sock.getpeername()), lv='dev', cat='foundation.tcp')
                    sock.send(to_send)

                if sock in self.outbound:
                    del (self.outbound[sock])

            except BlockingIOError as err:
                logger.ods('BlockingIOError @ [_proc_output]', lv='dev', cat='foundation.tcp')
            except Exception as err:
                logger.oes("", lv='error', cat='foundation.tcp')
                self._clear_peer(sock)

    def _proc_exception(self, xlist):
        for sock in xlist:
            logger.ods("exception condition on " + str( sock.getpeername()), lv='dev', cat='foundation.tcp')
            self._clear_peer(sock)

    def do_select_comm(self):
        try:
            self.s_lock.acquire()

            try:
                inputready, outputready, exceptrdy = select.select(self._get_inputs(), self._get_outputs(), self._get_inputs(), 0.1)

                self._proc_input(inputready)
                self._proc_output(outputready)
                self._proc_exception(exceptrdy)

                for sock in self.inbound:
                    if self._chk_to_close(sock):
                        self._clear_peer(sock)

            except Exception as err:
                logger.oes("do_select_comm failed", lv='error', cat='foundation.tcp')
                raise RuntimeError('[do_select_comm] failed.')
        finally:
            self.s_lock.release()


class _test_frame(object):

    def marshal(self):
        return bytes('show me the money'.encode('utf-8'))


def _test_decoder(data_in):
    if len(data_in) < 5:
        return 0, None
    print(str(data_in[0:5]))
    return 5,  str(data_in[0:5])


if __name__ == '__main__':
    server = SelectServer(frame_decoder=_test_decoder)
    while True:
        server.do_select_comm()
        #logger.ods ("123",lv='dev',cat = 'foundation.tcp'  )
        in_frame = server.pop_inbound()
        if in_frame is not None:
            logger.ods(str(in_frame), lv='dev', cat='foundation.tcp')
            server.push_outbound(in_frame['peer'], _test_frame())
            # server.close_peer(in_frame['peer'])
