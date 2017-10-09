# -*- coding: utf-8 -*-

"""
Descriptions

# This is the frame details of the ICM which part of the HuaXia bank special service ESB.

Inbound request:
0       1               2               4               12                 16              20          size+20       size+22
+-------+---------------+---------------+---------------+------------------+---------------+ +-------------+ +-----------+
|header |    type       |    version    |     token     |     sequance     |      size     | |    payload  | | frame-end |
+-------+---------------+---------------+---------------+------------------+---------------+ +-------------+ +-----------+
octet    octet           short           longlong        long               long              size octets      2 octets

header: 1 byte, always 0x01
type:   1 byte ,message type.  
        0x01:icm pack(icp->icm(BAOWEN))  0x02:icm pack(icm->icp(BAOWEN))
        0x03:icm pack(icm->icp(ACCEPTED))  0x04:icm pack(icm->icp(REFUSED))
        0x05:icm pack(icp->icm(BAOWEN)) TP处理02时，不需要返回值
        if 03 or 04 , the message in payloads will describ the details.

version: 2 bytes,0-65535, midware/message version
token:  8 bytes, peer token , not support yet. always 0x000x000x000x000x000x000x000x00
sequance: 4bytes, unique id to distinguish message peers .  server sends back message with the same sequance number as request.
size : 4bytes, payload length, in bytes .
palyload : .....
frame-end :  2bytes , always 0x57, 0x53('WS')


payload:
ICPs -> ICM
0            15         size+15     
+-------------+ +-----------+      
|      ID     | |  message  |      
+-------------+ +-----------+      
 octets           size octets 

ID: 16 bytes, string , max length is 16, if less than 16 charecters , the remains will be filled up with 0x00.
    this ID represents the commnode , and will be used in distinguishing which unpack method will be applied on the message.
message:    the message received by ICPs, and will be forwarded to the ICM . (jie shou dao de bao wen).



ICM -> ICPs
0            15         size+15     
+-------------+ +-----------+      
|      ID     | |  message  |      
+-------------+ +-----------+      
 octets           size octets 

id: 16 bytes, string , max length is 16, if less than 16 characters , the remains will be filled up with 0x00.
message:    the message will be sent back to ICPs.  (xiang ying ma@ yao fa song de bao wen )
formation of message :
message is a string that is the message(Bao Wen.)
only Exception is the TIMEOUT message starts with 'Timeout@'
for example : "Timeout@some description about the reason."





"""
import struct

from cpos.foundation.substrate.interfaces import *

class FrameException(Exception):
    pass
    


class ICMFrame(Monitored):
    NAME = 'ICMFrame'
    def __init__(self, frame_header=0x01, frame_type=0x01, frame_version=0x0001, token = None,
                    sequance = 0x00000000, payload = None ):
        super(ICMFrame,self).__init__()
        self.frame_header = frame_header
        self.frame_version = frame_version
        self.frame_type = frame_type
        self.token = token or bytes([0,0,0,0,0,0,0,0])
        self.sequance = sequance
        self.payload = payload or bytes([])
        self.payload_size = len(self.payload)


    def marshal(self):
        FMS = str(len( self.payload ) ) + 's'
        return struct.pack('>BBH8sII' + FMS + '2s', self.frame_header,self.frame_type,self.frame_version 
        , self.token 
        , self.sequance,self.payload_size
        , self.payload ,str('WS').encode(encoding="utf-8") )

def icm_decode_frame (data_in):

    try:
        (frame_header,frame_type,frame_version,token,sequance,payload_size) = struct.unpack('>BBH8sII', data_in[0:20])
    except struct.error:
        #print ('icm_decode_frame > struct.error')
        return 0, None

    frame_end = 20 + payload_size + 2

    if frame_end > len(data_in):
        return 0, None

    if chr(data_in[frame_end - 2]) !=  'W'  and chr(data_in[frame_end - 1]) !=  'S' :
        raise FrameException("Invalid FRAME_END marker")

    payload = data_in[20:frame_end - 2]

    return frame_end, ICMFrame(frame_header,frame_type,frame_version,token,sequance,payload)


#unpack_id must be a string that shorter than or equal to 16bytes 
def icm_decode_frame_payload (payload):
    commnode_id = ''
    message_body = b''
    try:
        (commnode_id,) = struct.unpack('>16s', payload[0:16])
    except struct.error as err:
        #print ('icm_decode_frame_payload > struct.error')
        return '' , ''


    message_body = payload[16:]
    return commnode_id.decode('utf-8').rstrip('\x00') , message_body

def icm_encode_frame_payload (commnode_id,message_body):
    FMS = str(len( message_body ) ) + 's'

    return struct.pack('>16s' + FMS , commnode_id.encode('utf-8'),message_body )


def build_icm_frame(commnode_id,message_body,frame_type=0x01,sequance = 0x00000001):
    pl = icm_encode_frame_payload(commnode_id,message_body)
    icm_frame = ICMFrame(frame_header=0x01, frame_type=frame_type, frame_version=0x0001, 
                            token = bytes([1,1,1,1,1,1,1,1]),sequance = sequance, payload = pl )
    return icm_frame

if __name__ == '__main__':

    fe, df =  icm_decode_frame ( build_icm_frame('nodeid_123','AB中国EFG'.encode('utf8')).marshal()     )  
    print (fe)
    print (df)
    print ( icm_decode_frame_payload( df.payload)[0] )
    print ( icm_decode_frame_payload( df.payload)[1] .decode('utf8') )
