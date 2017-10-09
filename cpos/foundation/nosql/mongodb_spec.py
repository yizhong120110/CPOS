# -*- coding: utf-8 -*-

"""
Inbound request:
0       4          8        8+keylen   8+keylen+valuelen   40+keylen+valuelen   41+keylen+valuelen
+-------+----------+-------------+---------------+------------------+---------------+
|keylen | valuelen |     key     |     value     |        md5       |      flag     |
+-------+----------+-------------+---------------+------------------+---------------+
   long   long      keylen octets  valuelen octets    32 octets           1 byte

"""
import struct
import hashlib
import pickle
import uuid
from ..substrate.interfaces import Monitored
from ..substrate.utils.logger import logger


class MongodbFrame(Monitored):
    NAME = 'MongodbFrame'

    def __init__(self, key_bytes=bytes([]), value_bytes=bytes([]), flag=0x00):
        super(MongodbFrame, self).__init__()
        self.key_bytes = key_bytes
        self.value_bytes = value_bytes
        self.key_len = len(self.key_bytes)
        self.value_len = len(self.value_bytes)
        self.md5 = hashlib.md5(key_bytes+value_bytes).hexdigest().encode('utf8')
        self.flag = 0

    def marshal(self):
        FMS_KEY = str( self.key_len) + 's'
        FMS_VALUE = str( self.value_len) + 's'
        return struct.pack('>II' + FMS_KEY + FMS_VALUE + '32sB', self.key_len, self.value_len, self.key_bytes, self.value_bytes, self.md5, self.flag)


def build_mongodb_frame(message_body, key_str=''):
    """
        传入内容、key，构建结构体
    """
    if not key_str:
        key_str = uuid.uuid4().hex
    key_str = str(key_str).encode('utf8')
    mongodb_frame = MongodbFrame(key_bytes=key_str, value_bytes=pickle.dumps(message_body))
    return mongodb_frame


def decode_mongodb_frame(fileobj):
    """
        传入一个文件操作对象，对这个对象做结构体解析
    """
    # keystr和valobj的长度域 2个long
    rd_data = fileobj.read(4*2)
    if rd_data == b'':
        return None, None, None

    # 长度域
    (keystr_len, valobj_len,) = struct.unpack('>II', rd_data)
    # 实际值、md5、flag标志位
    rd_data = fileobj.read(keystr_len+valobj_len+32+1)
    (keystr, valobj, md5str, flag,) = struct.unpack('>%ss%ss32sB' % (keystr_len, valobj_len), rd_data)

    # md5检查失败
    md5_rd = hashlib.md5(keystr+valobj).hexdigest().encode('utf8')
    if md5_rd != md5str:
        msgstr = "文件损坏，文件中MD5为[%s]，实际MD5为[%s]" % (md5_rd, md5str)
        logger.ods(msgstr, lv='warning', cat='foundation.mgodb')
        return None, None, "error"
    return keystr.decode('utf8'), pickle.loads(valobj), flag


def readfile(filepath):
    fb = open(filepath, 'rb')
    while True:
        keystr, valobj, flag = decode_mongodb_frame(fb)
        if flag == None:
            break
        print(keystr, valobj)
#        print(build_mongodb_frame(valobj ,keystr).marshal())
    fb.close()


if __name__ == '__main__':
    print(str(build_mongodb_frame('AB中国EFG')))
    readfile(r"F:\Projects_TEMP\translog\2015-07-06\ltdls_tx\324651.log")
