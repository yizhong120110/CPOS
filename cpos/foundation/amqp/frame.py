#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import struct

from . import amqp_object
from . import exceptions
from . import spec
from ..substrate.utils.logger import logger


def ch2bytes(x):
    res = str(chr(x)).encode(encoding="utf-8")
    return res, len(res)


def str2bytes(x):
    res = x.encode(encoding="utf-8")
    return res, len(res)


def dump_hex(bytes):
    output = ''
    for b in bytes:
        output += '%02X' % b
        output += '('
        if b >= 32 and b <= 126:
            output += str(chr(b))
        output += ')'
        output += '\t'
    logger.ods(output, lv='test', cat='foundation.amqp')
    logger.ods('------------------------------------------', lv='test', cat='foundation.amqp')


def dump_hex_list(bl):
    logger.ods('dumping hex list:', lv='test', cat='foundation.amqp')
    for b in bl:
        dump_hex(b)
    logger.ods('------------------------------------------', lv='test', cat='foundation.amqp')


class Frame(amqp_object.AMQPObject):

    """Base Frame object mapping. Defines a behavior for all child classes for
    assignment of core attributes and implementation of the a core _marshal
    method which child classes use to create the binary AMQP frame.

    """
    NAME = 'Frame'

    def __init__(self, frame_type, channel_number):
        """Create a new instance of a frame

        :param int frame_type: The frame type
        :param int channel_number: The channel number for the frame

        """
        self.frame_type = frame_type
        self.channel_number = channel_number

    def _marshal(self, pieces):
        """Create the full AMQP wire protocol frame data representation

        :rtype: str

        """
        bs = bytes()
        payload = bs.join(pieces)
        #payload = ''
        # for p in pieces:
        #    payload += str(p)

        #payload_bytes, payload_len = str2bytes(payload)
        FMS = str(len( payload)) + 's'

        #print('Ready to be packed : ' )
        # dump_hex(payload)
        return struct.pack('>BHL'+FMS + 'B',
                           self.frame_type,
                           self.channel_number,
                           len( payload), payload, spec.FRAME_END)

    def marshal(self):
        """To be ended by child classes

        :raises NotImplementedError

        """
        raise NotImplementedError


class Method(Frame):

    """Base Method frame object mapping. AMQP method frames are mapped on top
    of this class for creating or accessing their data and attributes.

    """
    NAME = 'METHOD'

    def __init__(self, channel_number, method):
        """Create a new instance of a frame

        :param int channel_number: The frame type
        :param Spec.Class.Method method: The AMQP Class.Method

        """
        Frame.__init__(self, spec.FRAME_METHOD, channel_number)
        self.method = method

    def marshal(self):
        """Return the AMQP binary encoded value of the frame

        :rtype: str

        """
        pieces = self.method.encode()
        pieces.insert(0, struct.pack('>I', self.method.INDEX))
        return self._marshal(pieces)


class Header(Frame):

    """Header frame object mapping. AMQP content header frames are mapped
    on top of this class for creating or accessing their data and attributes.

    """
    NAME = 'Header'

    def __init__(self, channel_number, body_size, props):
        """Create a new instance of a AMQP ContentHeader object

        :param int channel_number: The channel number for the frame
        :param int body_size: The number of bytes for the body
        :param spec.BasicProperties props: Basic.Properties object

        """
        Frame.__init__(self, spec.FRAME_HEADER, channel_number)
        self.body_size = body_size
        self.properties = props

    def marshal(self):
        """Return the AMQP binary encoded value of the frame

        :rtype: str

        """
        pieces = self.properties.encode()
        pieces.insert(0, struct.pack('>HxxQ',
                                     self.properties.INDEX,
                                     self.body_size))
        return self._marshal(pieces)


class Body(Frame):

    """Body frame object mapping class. AMQP content body frames are mapped on
    to this base class for getting/setting of attributes/data.

    """
    NAME = 'Body'

    def __init__(self, channel_number, fragment):
        """
        Parameters:

        - channel_number: int
        - fragment: unicode or str
        """
        Frame.__init__(self, spec.FRAME_BODY, channel_number)
        self.fragment = fragment

    def marshal(self):
        """Return the AMQP binary encoded value of the frame

        :rtype: str

        """
        return self._marshal([self.fragment])


class Heartbeat(Frame):

    """Heartbeat frame object mapping class. AMQP Heartbeat frames are mapped
    on to this class for a common access structure to the attributes/data
    values.

    """
    NAME = 'Heartbeat'

    def __init__(self):
        """Create a new instance of the Heartbeat frame"""
        Frame.__init__(self, spec.FRAME_HEARTBEAT, 0)

    def marshal(self):
        """Return the AMQP binary encoded value of the frame

        :rtype: str

        """
        return self._marshal(list())


class ProtocolHeader(amqp_object.AMQPObject):

    """AMQP Protocol header frame class which provides a pythonic interface
    for creating AMQP Protocol headers

    """
    NAME = 'ProtocolHeader'

    def __init__(self, major=None, minor=None, revision=None):
        """Construct a Protocol Header frame object for the specified AMQP
        version

        :param int major: Major version number
        :param int minor: Minor version number
        :param int revision: Revision

        """
        self.frame_type = -1
        self.major = major or spec.PROTOCOL_VERSION[0]
        self.minor = minor or spec.PROTOCOL_VERSION[1]
        self.revision = revision or spec.PROTOCOL_VERSION[2]

    def marshal(self):
        """Return the full AMQP wire protocol frame data representation of the
        ProtocolHeader frame

        :rtype: str

        """
        return str('AMQP').encode(encoding="utf-8") + struct.pack('BBBB', 0,
                                                                  self.major,
                                                                  self.minor,
                                                                  self.revision)


def amqp_decode_frame(data_in):
    """Receives raw socket data and attempts to turn it into a frame.
    Returns bytes used to make the frame and the frame

    :param str data_in: The raw data stream
    :rtype: tuple(bytes consumed, frame)
    :raises: exceptions.InvalidFrameError

    """
    # Look to see if it's a protocol header frame
    try:
        if str(data_in[0:4]) == 'AMQP':
            major, minor, revision = struct.unpack_from('BBB', data_in, 5)
            return 8, ProtocolHeader(major, minor, revision)
    except (IndexError, struct.error):
        return 0, None

    try:
        (frame_type,
         channel_number,
         frame_size) = struct.unpack('>BHL', data_in[0:7])
    except struct.error:
        return 0, None

    frame_end = spec.FRAME_HEADER_SIZE + frame_size + spec.FRAME_END_SIZE

    if frame_end > len(data_in):
        return 0, None

    if chr(data_in[frame_end - 1]) != chr(spec.FRAME_END):
        raise exceptions.InvalidFrameError("Invalid FRAME_END marker")

    frame_data = data_in[spec.FRAME_HEADER_SIZE:frame_end - 1]

    if frame_type == spec.FRAME_METHOD:

        method_id = struct.unpack_from('>I', frame_data)[0]
        method = spec.methods[method_id]()
        method.decode(frame_data, 4)
        return frame_end, Method(channel_number, method)

    elif frame_type == spec.FRAME_HEADER:
        class_id, weight, body_size = struct.unpack_from('>HHQ', frame_data)
        properties = spec.props[class_id]()
        out = properties.decode(frame_data[12:])
        return frame_end, Header(channel_number, body_size, properties)

    elif frame_type == spec.FRAME_BODY:
        return frame_end, Body(channel_number, frame_data)

    elif frame_type == spec.FRAME_HEARTBEAT:
        return frame_end, Heartbeat()

    raise exceptions.InvalidFrameError("Unknown frame type: %i" % frame_type)


if __name__ == '__main__':
    p = ProtocolHeader()
    dump_hex(p.marshal())

    ff = Frame(254, 65533)
    dump_hex(ff._marshal(['hello'.encode(encoding='utf-8'), 'world'.encode(encoding='utf-8')]))

    b = spec.Connection.Start()
    f = Method(65533, b)

    dump_hex_list(b.encode())
    dump_hex(f.marshal())
