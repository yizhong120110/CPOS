# -*- coding: utf-8 -*-
""" 
    LP 
      将RPC中的日志内容转到mongodb中
      1.判断消息中的消息类型logtype；
      2.若logtype值为translog（交易产生的log），使用MongodbLog类将log信息记录到Mongodb数据库中。
      3.其他类型的log（进程log或响应动作log），用with connection的方式，将log信息记录到rdb数据库pro_xxhb表中。
"""
from cpos.esb.basic.resource.nosql import get_mlobj
import os

def content2logdb(content):
    """
        # content = {"logcontent":logcontent, "logtype":"translog", "_id":str(uuid.uuid1())}
    """
    if content.get('logtype') == 'translog':
        # 交易中的日志信息要存到mongodb中
        ml = get_mlobj(str(content['logtype']))
        content['lppid'] = os.getpid()
        content['writetype'] = "log_rpc"
        rs = ml.writedata(content['_id'], content)
        ml.close()
        return rs
    else:
        # 系统运行产生的自动汇报信息，需要保存吗？
        return None
