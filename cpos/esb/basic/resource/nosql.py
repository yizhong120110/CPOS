# -*- coding: utf-8 -*-
from cpos.foundation.nosql.mgodb import MongodbLog
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.config import settings
import re


def get_mlobj(typestr):
    """
        获得mongodb的连接对象
    """
    ml = None
    try:
        mlparas = settings.LOG_MAP_DIC[typestr]
        ml = MongodbLog(mlparas["local_file"], settings.MONGODB_IPS, mlparas["dbname"], mlparas["collection"])
        ml.openconn()
    except:
        logger.oes( str(typestr) + " mongodb连接失败",lv = 'error',cat = 'resource.nosql')
    return ml


def readlog(rq,lsh,jdid=None):
    """
        # rq（交易日期，必填）、
        # lsh（交易流水号，必填）、
        # jdid（交易节点编码，非必填）
    """
    ml = get_mlobj("translog")
    query = {'logcontent.jyrq':rq,'logcontent.lsh':lsh}
    if jdid is not None:
        # 提供did="ltjf_zlc.ltjf_zlc.dsyw_pack_beai_510001"
        jdid = jdid.replace('.',r"\|")
        # jdid=r"ltjf_zlc\|ltjf_zlc\|dsyw_pack_beai_510001"  这样查询
        query['logcontent.jdid'] = re.compile(r'^'+jdid+'.*')
    aaaa = ml.find(query,sort=[("logcontent.sj",1),("logcontent.msgxh",1)])
    ml.close()
    rs = []
    for row in aaaa:
        rs.append(row['logcontent'])
    return rs


def readlog_syslog(rq ,hostname ,logtype="syslog" ,level=None ,pid=None ,rqsjbase=None):
    """
       读syslog日志
       readlog_syslog("2015-08-14" ,"shhx233" ,logtype="syslog" ,level=None ,pid="6994" ,rqsjbase="2015-08-14 13:37:46.000000"
    """
    ml_sys = get_mlobj("syslog")
    query = {'logcontent.rq':rq,'hostname':hostname ,'logtype':logtype}
    if level:
        query['logcontent.level'] = level
    if pid:
        query['logcontent.pid'] = pid
    if rqsjbase:
        query['logcontent.sj'] = {'$gt':rqsjbase}
    aaaa = ml_sys.find(query,sort=[("logcontent.pid",1),("logcontent.sj",1)])
    ml_sys.close()
    rs = []
    for row in aaaa:
        rs_str = " | ".join([row["hostname"] ,row["logcontent"]["sj"] ,row["logcontent"]["pid"] ,row["logcontent"]["level"] ,row["logcontent"]["cat"] ,row["logcontent"]["msg"]])
        rs.append(rs_str)
    return rs
########################################################################################################
def test_readlog():
    # 这是先赋值
    print ('查询数据')
    print(readlog(rq='2015-03-11',lsh='201503100001101010',jdid='aaaaa'))
    print(readlog(rq='2015-03-11',lsh='201503100001101010'))
    print(readlog(rq='2015-03-12',lsh='201503101012101010'))


if __name__=="__main__":
    for i in readlog(rq='20150320',lsh='448',jdid="ltjf_zlc.ltjf_zlc.dsyw_pack_beai_510001"):
        print(i)

