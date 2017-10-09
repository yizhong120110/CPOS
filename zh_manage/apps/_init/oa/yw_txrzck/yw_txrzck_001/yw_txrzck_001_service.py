# -*- coding: utf-8 -*-
# Action: 通讯日志查看 主页面 service
# Author: psnsy
# AddTime: 2016-01-21
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql, get_sess_hydm, logger
from sjzhtspj.common import get_strftime, get_uuid, ins_czrz, update_wym, py_check, get_bmwh_bm,get_strfdate
import pickle, json
from sjzhtspj.esb import transaction_test,memcache_data_del
from optparse import OptionParser
import os
import time
import datetime
import re
import pymongo

# 连接mongodb时使用的配置
MONGODB_IPS = []
MONGODB_DBNAME = "zhtsyw"
MONGODB_COLLECTION = "translog"

def data_service( data_dic ):
    """
    # 通讯日志查看-通讯展示 列表初始化 service
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    # 数据库操作
    with sjapi.connection() as db:
        
        # 查询通讯总条数
        total = ModSql.yw_txrzck_001.execute_sql( db, 'data_count' )[0].count
        # 查询通讯列表信息
        sql_dic = { 'rn_start': data_dic['rn_start'], 'rn_end': data_dic['rn_end'] }
        txglxx = ModSql.yw_txrzck_001.execute_sql_dict( db, 'data_rs', sql_dic )
        
        #组织反馈信息
        data['total'] = total
        data['rows'] = txglxx
        # 当前日期
        data['nowdate'] = get_strfdate()
        
    return data
    
def get_ip():
    """
    # 获取连接mongodbIP
    """
    with sjapi.connection() as db:
        # 查询通讯列表信息
        ip = ModSql.yw_txrzck_001.execute_sql( db, 'get_ip' )[0].value
        # 连接mongodb时使用的配置
        ip = ['%s:5625' % ip]
        return ip
        
def get_rz_service( data_dic ):
    """
    # 获取日志 service
    """
    # 反馈信息
    data = ''
    # 获取日志
    data = rz_main( data_dic )
    return data
    
def get_shell_args( data_dic ):
    """
        获得程序启动使用到的参数
        {'sorttype': 'pid_time', 'basesj': '2015-09-12 13:21:33.000000',
             'fdate': '20150912', 'level': 'INFO', 'outfn':'20150912.log'}
    """
    jyrq = data_dic['jyrq']
    kssj = data_dic['kssj']
    jssj = data_dic['jssj']
    txwjmc = data_dic['txwjmc']
    options = {}
    options['fdate'] = jyrq
    options['outfn'] = "%s.log"%jyrq
    options['sorttype'] = "time_pid"
    options['level'] = ''
    options['basesj'] = datetime.datetime.strptime("%s %s"%(jyrq,kssj),'%Y%m%d %H%M%S').strftime('%Y-%m-%d %H:%M:%S.000000')
    if jssj == '':
        options['endsj'] = datetime.datetime.strptime("%s %s"%(jyrq,'235959'),'%Y%m%d %H%M%S').strftime('%Y-%m-%d %H:%M:%S.999999')
    else:
        options['endsj'] = datetime.datetime.strptime("%s %s"%(jyrq,jssj),'%Y%m%d %H%M%S').strftime('%Y-%m-%d %H:%M:%S.000000')
    options['kind'] = txwjmc
    return options

def out2file(mongodbrs):
    """
        将 mongodb的查询结果格式化，返回前台
    """
    log_str = """"""
    line = 0
    try:
        for row in mongodbrs:
            line += 1
            rs_str = str(line).rjust(5) + " " +  " | ".join([row["logcontent"]["sj"] ,row["logcontent"]["level"] ,row["logcontent"]["lsh"] ,row["logcontent"]["msg"]])
            log_str += rs_str
        return log_str
    except:
        return 'error'


def get_mlobj(connlst=MONGODB_IPS ,dbname=MONGODB_DBNAME ,collection=MONGODB_COLLECTION):
    """
        获得mongodb的连接对象
    """
    conn = pymongo.Connection(','.join(connlst) ,read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED)
    coll = conn[dbname][collection]
    return coll

def readlog_translog(kwd):
    """
       读mongodb中的syslog日志
        {'sorttype': 'pid_time', 'hostname': None, 'pid': 9034, 'basesj': '2015-09-12 13:21:33.000000',
             'fdate': '2015-09-12', 'level': 'INFO', 'outfn':'20150912.log'}
    """
    
    ip = get_ip()
    ml_sys = get_mlobj(connlst=ip)
    query = {'logcontent.jyrq':kwd["fdate"]}
    if kwd.get("level"):
        query['logcontent.level'] = kwd["level"]
    if kwd.get("kind"):
        query['logcontent.kind'] = kwd["kind"]
    if kwd.get("basesj"):
        if kwd.get("endsj"):
            query['logcontent.sj'] = {'$gt':kwd["basesj"],'$lt':kwd["endsj"]}
        else:
            query['logcontent.sj'] = {'$gt':kwd["basesj"]}
    print('查询字段：%s'%query)
    mongodbrs = ml_sys.find(query,sort=[("logcontent.sj",1),("logcontent.msgxh",1)])


    return mongodbrs


def rz_main( data_dic ):
    opts = get_shell_args( data_dic )
    mongodbrs = readlog_translog(opts)
    log = out2file(mongodbrs)
    return log
