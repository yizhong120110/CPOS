# -*- coding: utf-8 -*-

# mongodb记录日志的操作
# 应该考虑对于异常的处理，如果mongodb连接失败，
#    那么应该将文件写到本地的二进制文件中，在数据库连接成功后再写入到数据库中，
#    需要确定二进制文件的数据格式，可以参考交易类的变长报文的概念；
#    对于数据应该写入到什么表、用户下，可以通过配置文件配置；
#    如何操作数据呢？进行查询操作
# 应该指定id的值，如果没有指定的话可以使用uuid？？这个是不是和业务相关了？

import pymongo
from bson.binary import Binary
import copy
import os
import struct
from .mongodb_spec import build_mongodb_frame, decode_mongodb_frame
from ..system import locker
from ..substrate.utils.logger import logger


def bytes2Binary(dict_obj):
    """
        将bytes型的value做一次类型转换，变为 Binary('中国'.encode('utf8'), 0)
        不考虑key不是str的情况
    """
    rs_dict = {}
    for kk in dict_obj.keys():
        if isinstance(dict_obj[kk], dict):
            val = bytes2Binary(dict_obj[kk])
        elif isinstance(dict_obj[kk], bytes) or isinstance(dict_obj[kk], bytearray):
            val = Binary(bytes(dict_obj[kk]), 0)
        else:
            val = dict_obj[kk]
        rs_dict[kk] = val
    return copy.deepcopy(rs_dict)


class MongodbLog(object):

    """
        # 每次使用连接的时候再创建连接
        # 如果没有连接串、或者连接时操作失败，则写到本地文件
        # 先尝试进行连接处理，如果不行则写本地文件，然后尝试将本地文件写到mongodb中
        # 本地文件按照高字节序处理，为了能够跨平台使用

        # 说明应该在 __init__ 中做检查的
        # 应该检查一下localdbpath是否可以使用，如果不能够使用，则应该使用默认位置
            # 考虑到文件权限的问题，不提供默认位置
        # 可能存在一个情况，mongodb能够使用，本地文件不能使用，应该只输出错误信息
            # 启动时直接检查mongodb的本地缓存文件目录是否存在，如果不存在则直接提示错误，不检查mongodb是否可以连接
        # 如果local文件可以使用，mongodb不能使用，这个只输出错误信息就行

    """

    def __init__(self, localdbpath, connlst, dbname="admin", collection="sjlogdb"):
        """
            # @Param connlst: ['127.0.0.1:10001','127.0.0.1:11001']
            # conn 类型<class 'pymongo.connection.Connection'>
        """
        self.connlst = connlst
        # mongodb使用的用户名
        self.dbname = dbname
        self.collection = collection
        self.conn = None
        self.coll = None

        # 本地缓存文件的位置
        if os.path.isdir(localdbpath) == False:
            try:
                logger.ods("[ %s ]目录不存在，自动创建" % localdbpath, lv='info', cat='foundation.mgodb')
                os.makedirs(localdbpath)
                logger.ods("目录创建完毕", lv='info', cat='foundation.mgodb')
            except:
                logger.ods("目录创建失败", lv='info', cat='foundation.mgodb')
        self.filepath = self.get_localfilepath(localdbpath)

    def __del__(self):
        self.close()

    def close(self):
        # 可能没有能够创建出该链接，所以不用关闭
        try:
            if self.conn:
                self.conn.close()
            if os.path.isfile(self.filepath) == True and os.path.getsize(self.filepath) == 0:
                # 缓存文件存在，且内容为空，将其删除
                os.remove(self.filepath)
        except:
            pass

    def openconn(self):
        try:
            if self.coll is None:
                self.conn = pymongo.Connection(','.join(self.connlst), read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED)
                self.coll = self.conn[self.dbname][self.collection]
        except:
            msgstr = 'connect to %s %s %s error' % (self.connlst, str(self.dbname), str(self.collection))
            logger.ods(msgstr, lv='warning', cat='foundation.mgodb')

    def get_localfilepath(self, localdbpath):
        """
            应该提供一个Windows和Linux上的默认位置
        """
        # 本地的缓存文件，属于固定名称
        filename = 'Mongodb.%s.local' % (self.collection)
        return os.path.join(localdbpath, filename)

    def writedata(self, keystr, valobj):
        if not isinstance(valobj, dict):
            # valobj 必须是dict型的，否则不能写入数据
            logger.ods("仅能保存字典型数据，且_id为系统关键字", lv='warning', cat='foundation.mgodb')
            return None

        if os.path.isfile(self.filepath):
            # 如果缓存文件存在，则将数据写入到缓存文件中，然后将缓存文件中的内容写入到服务器
            self.writedata2file(keystr, valobj)
        else:
            # 如果缓存文件不存在，则直接写数据库
            if self.id_setdefault(keystr, valobj) is None:
                # 写入mongodb失败，转到本地文件中
                self.writedata2file(keystr, valobj)

        if os.path.isfile(self.filepath) == True:
            # 存在本地缓存文件，处理一下
            self.writefile2db()
        return True

    def id_setdefault(self, keystr, valobj):
        """
            # 通过id的方式进行数据insert，如果数据已存在，则进行update操作
            # valobj 必须是dict型的，且不能够使用 _id 这一key名
            # return None：失败   1：insert成功   2：update成功
        """
        self.openconn()
        if self.coll is None:
            return None
        try:
            valobj['_id'] = keystr
            # 为了保证bytes类型的数据能够写入到mongodb中
            valobj_Binary = bytes2Binary(valobj)
            if self.coll.find({'_id': keystr}).count() == 0:
                self.coll.insert(valobj_Binary)
                return 1
            else:
                self.coll.update({'_id': keystr}, valobj_Binary)
                return 2
        except pymongo.errors.DocumentTooLarge:
            logger.oes("日志内容将被丢弃", lv='error', cat='foundation.mgodb')
            return 3
        except:
            logger.oes("数据保存失败", lv='error', cat='foundation.mgodb')
            return None

    def writedata2file(self, keystr, valobj):
        """
            # 将传入的内容通过json方式进行转化保存
            # 二进制的记录规格：
            #     主键值的长度域（4字节），内容值的长度域的长度（4字节），
            #     主键值（json，变长），内容值（json，变长），
            #     登记时间 2015-02-07 16:33:12 656   # 只有一个二进制文件，固定名称，不会出现需要判断更新时间的问题，删掉
            #     MD5（32字节，主键值、内容值），
            #     标志位 1字节  0:待处理  1:写入到数据库中   在读取数据内容写入到数据库中的时候会起作用
            # PS：struct.pack('l',1)  在windwos、linux、AIX上的输出结果不同，所以生成的文件不能够跨平台移动
            #        应该统一按照网络字节序处理，使用高位在前的方式，应该打包、解包的时候加">"，具体需要看文档
        """
        try:
            rsstr = build_mongodb_frame(valobj, key_str=keystr)

            # 由于flock生成的是劝告锁，不能阻止进程对文件的操作，所以这里可以正常打开文件
            with open(self.filepath, 'ab') as fileobj:
                # 为了避免同时操作文件，需要程序自己来检查该文件是否已经被加锁。这里如果检查到加锁了，进程会被阻塞
                locker.lock(fileobj, locker.LOCK_EX)
                fileobj.write(rsstr.marshal())
            return True
        except:
            msgstr = "数据库、本地文件均保存失败"
            logger.ods(msgstr, lv='error', cat='foundation.mgodb')
            raise RuntimeError(msgstr)
            return False

    def writefile2db(self):
        self.writefile2db_file(self.filepath)

    def writefile2db_file(self, filepath, valfunc=None, newfile=None):
        """
            # 这是一个循环处理的过程，文件中的内容由多条数据组成
            # 在将本地文件中数据保存到数据库中以后，利用seek将本地文件中的flag标记更新
            # 一个文件中的所有记录的flag都更新后，将文件内容清空
        """
        try:
            # 由于flock生成的是劝告锁，不能阻止进程对文件的操作，所以这里可以正常打开文件
            with open(filepath, 'r+b') as fileobj:
                # 为了避免同时操作文件，需要程序自己来检查该文件是否已经被加锁。这里如果检查到加锁了，进程会被阻塞
                locker.lock(fileobj, locker.LOCK_EX)
                while True:
                    keystr, valobj, flag = decode_mongodb_frame( fileobj)
                    if flag == "error":
                        # 文件出错了，不再继续处理
                        break

                    if flag == None:
                        # 内容结束了，说明flag均变为1了，将文件内容清空
                        fileobj.seek(0, 0)
                        if newfile:
                            os.makedirs(os.path.dirname(newfile), exist_ok=True)
                            open(newfile, 'ab').write(fileobj.read())
                            fileobj.seek(0, 0)
                        fileobj.truncate()
                        fileobj.flush()
                        break

                    if flag == 0:
                        if valfunc:
                            # 需要在写入mongodb前做一下数据加工
                            valobj = valfunc(valobj)
                        rs = self.id_setdefault( keystr, valobj)
                        if rs == None:
                            break
                        if rs > 0:
                            # 写入成功
                            fileobj.seek(-1, 1)
                            # 更新文件中记录的标志位
                            fileobj.write(struct.pack('>b', 1))
                            fileobj.flush()
            return True
        except FileNotFoundError:
            # 不需要记录异常，这个之后还能处理
            logger.ods("缓存文件【%s】不存在，可能已被加锁" % (filepath), lv='warning', cat='foundation.mgodb')
            return False
        except:
            logger.oes("缓存文件转移失败【%s】" % (filepath), lv='error', cat='foundation.mgodb')
            return False

    def find(self, query={}, sort=[]):
        """
            # 查询文档的内部结构 ml.find({'valobj.lsh':'58001'}) 可以封装一下，对lsh做针对性查询
            # 注意这里query是dict类型
            # 模糊查询处理方式：
            #    1、find('lsh':{'$regex':'80'})) ==》 lsh like '%80%'
            #    2、find({'lsh':re.compile(r'(\d{4})-(\d{2})-(\d{2})')})) ==》 通过正则方式匹配 YYYY-MM-DD 格式的串
        """
        result = []
        if type(query) is not dict:
            logger.ods('the type of query isn\'t dict', lv='warning', cat='foundation.mgodb')
            exit(0)
        try:
            # result类型<class 'pymongo.cursor.Cursor'>
            if not self.coll:
                logger.ods('don\'t assign collection', lv='info', cat='foundation.mgodb')
            else:
                result = self.coll.find(query, sort=sort)
        except NameError:
            logger.ods('some fields name are wrong in ' + str(query), lv='error', cat='foundation.mgodb')
            exit(0)
        return result


if __name__ == "__main__":
    import uuid
    import time

    mlparas = {"local_file": r"E:\TDDOWNLOAD",  # '/home/oa_manage_sj/log/testmgo',
               "mongodb_ips": ['127.0.0.1:10101'],     # ['46.17.189.236:10001'],
               'dbname': "sjdev", 'collection': "sjdev_defalut"}
    ml = MongodbLog(mlparas["local_file"], mlparas["mongodb_ips"], mlparas["dbname"], mlparas["collection"])
    content = {"_id": str(uuid.uuid1()), 'cnt': str(time.time()), 'bytestest222': '中国'.encode('utf8')}
    print(ml.writedata(content['_id'], content))
    content = {"_id": "4607047a-de60-11e4-82b6-b888e3f7504b", 'cnt': str(time.time())}
    print(ml.writedata(content['_id'], content))

    print("=====================用于查询数据，检查insert结果")
    for row in ml.find(sort=[("cnt", 1)]):
        print(row)
