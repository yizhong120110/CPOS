# -*- coding: utf-8 -*-

"""
Descriptions

Inbound request.
0       1               5          size+5        size+7
+-------+---------------+ +-------------+ +-----------+
|header |      size     | |    message  | | frame-end |
+-------+---------------+ +-------------+ +-----------+
octet          long           size octets     octet
;
header: 1 byte, always 0x01
size : 4bytes, message length, in bytes .
message : .....
frame-end :  2bytes , always 0x57, 0x53('WS')


message：
0          60        120          122         124             128       size1+128         size1+132   size1+size2+132
+-----------+----------+-----------+-----------+---------------+ +-------------+ ---------------+ +-------------+
|client_type| clientid | clientpid |   iswait  |      size1    | |    sysload  |       size2    | |    msgload  |
+-----------+----------+-----------+-----------+---------------+ +-------------+ ---------------+ +-------------+
   60bytes    60bytes       short       short          long           size octets       long           size octets
;
client_type: 60bytes
clientid: 60bytes
clientpid: 2 bytes,0-65535
iswait: 2 bytes,0-65535
size1 : 4bytes, msgload length, in bytes .
sysload : R to E ,system
size2 : 4bytes, msgload length, in bytes .
msgload : .....

"""
import struct
from ..substrate.interfaces import Monitored


class FrameException(Exception):
    pass


class INFrame(Monitored):
    NAME = 'INFrame'

    def __init__(self, frame_header=0x01, message=None):
        super(INFrame, self).__init__()
        self.frame_header = frame_header
        self.message = message or bytes([])
        self.message_size = len(self.message)

    def marshal(self):
        FMS = str(self.message_size) + 's'
        return struct.pack('>BI' + FMS + '2s', self.frame_header, self.message_size, self.message, str('WS').encode(encoding="utf-8"))


def decode_frame(data_in):
    """
        报文的帧结构构建
    """
    try:
        (frame_header, message_size) = struct.unpack('>BI', data_in[0:5])
    except struct.error:
        #print ('decode_frame > struct.error')
        return 0, None
    frame_end = 5 + message_size + 2
    if frame_end > len(data_in):
        return 0, None
    if chr(data_in[frame_end - 2]) != 'W' and chr(data_in[frame_end - 1]) != 'S':
        raise FrameException("Invalid FRAME_END marker")
    message = data_in[5:frame_end - 2]
    return frame_end, INFrame(frame_header, message)


def build_frame(message_body):
    """
        按照报文的域框架构建报文
        message_body：为str类型
    """
    in_frame = INFrame(0x01, message_body)
    return in_frame


class FrameMessage(Monitored):
    NAME = 'FrameMessage'

    def __init__(self, client_type='', clientid='', clientpid=0, iswait=1, sysload=None, msgload=None):
        super(FrameMessage, self).__init__()
        self.client_type = client_type
        self.clientid = clientid
        self.clientpid = clientpid
        self.iswait = iswait
        self.sysload = sysload or ''
        self.sysload_size = len(self.sysload.encode(encoding="utf-8"))
        self.msgload = msgload or ''
        self.msgload_size = len(self.msgload.encode(encoding="utf-8"))

    def marshal(self):
        FMS_SYS = str(self.sysload_size) + 's'
        FMS_MSG = str(self.msgload_size) + 's'
        return struct.pack('>60s60sHHI' + FMS_SYS + 'I' + FMS_MSG, self.client_type.encode(encoding="utf-8"), self.clientid.encode(encoding="utf-8"), self.clientpid, self.iswait, self.sysload_size, self.sysload.encode(encoding="utf-8"), self.msgload_size, self.msgload.encode(encoding="utf-8")
                           )


def decode_frame_message(data_in):
    """
        报文的内容传输部分
    """
    try:
        (client_type, clientid, clientpid, iswait, sysload_size) = struct.unpack('>60s60sHHI', data_in[0:128])
    except struct.error:
        raise
        #print ('decode_frame > struct.error')
        return None
    frame_end = 128 + sysload_size
    sysload = data_in[128:frame_end]
    try:
        (msgload_size,) = struct.unpack('>I', data_in[frame_end:frame_end+4])
    except struct.error:
        #print ('decode_frame > struct.error')
        return None
    frame_end += 4 + msgload_size
    msgload = data_in[frame_end-msgload_size:]
    return FrameMessage(client_type.decode("utf8").rstrip('\x00'), clientid.decode("utf8").rstrip('\x00'),
                        clientpid, iswait, sysload.decode('utf-8'), msgload.decode('utf-8'))


def build_frame_message(client_type, clientid, clientpid, message_body, sysload_body=None, iswait=1):
    """
        按照报文的域框架构建报文
        client_type：为str类型
        clientid：为str类型
        clientpid：为int类型
        message_body：为str类型
        sysload_body：为str类型
    """
    client_type = str(client_type or "")
    clientid = str(clientid or "")
    sysload_body = str(sysload_body or "")
    message_body = str(message_body or "")
    in_frame = FrameMessage( client_type=client_type, clientid=clientid, clientpid=clientpid, iswait=iswait, sysload=sysload_body, msgload=message_body)
    return in_frame.marshal()


def bfm(client_type, clientid, clientpid, iswait, message_body, sysload_body=None):
    """
        纯粹的快捷方式
    """
    return build_frame(build_frame_message( client_type, clientid, clientpid, message_body, sysload_body, iswait))


if __name__ == "__main__":
    d, e = decode_frame( bfm('0', '0', 0, 1, None, "中文测试").marshal())
    print(d)
    print(e)
    aa = decode_frame_message(e.message)
    print(aa)
    print(aa.sysload)
