# -*- coding: utf-8 -*-
# Action: 特色业务平台公共函数
# Author: zhangchl
# AddTime: 2015-07-29
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import hashlib
# 数据库连接
import ops.core.rdb
# 日志
from ops.core.logger import tlog


def cal_md5(obj):
    """
    # 计算传入对象的md5值
    # 先将传入对象做str()处理，再计算
    """
    return hashlib.md5(str(obj).encode('utf-8')).hexdigest()
    
def update_wym(cur, lx, id):
    """
    # 更新唯一码
    # db: 数据库连接
    # lx: 类型('jy':交易, 'zlc':子流程, 'jd':节点, 'gghs':公共函数(业务), 'sjk':数据库, 'txgl':通讯管理, 'cdtxgl':C端通讯管理, 'cs':参数, 'dy':打印配置)
    # id: 对应的ID（如lx是'jy'，则此处是交易ID）
    """
    tlog.log_info( '更新唯一码开始，类型:%s,id:%s' % ( lx, id ) )
    sql_data = {'id': id}
    # 交易唯一码：ID+所属业务ID+交易码+交易名称+交易描述+交易超时时间+交易状态+自动发起配置+流程布局表+流程走向表
    if lx == 'jy':
        tlog.log_info( '更新交易唯一码' )
        # 查询交易定义
        tlog.log_info( '查询交易定义start' )
        sql_jydy = """select id, ssywid, jym, jymc, jyms, timeout, zt, zdfqpz, dbjdid, jbjdid, zdfqpzsm
        from gl_jydy
        where id = '%s'""" % id
        cur.execute( sql_jydy )
        rs_jydy = cur.fetchall()
        tlog.log_info( '查询交易定义end' )
        # 查询流程布局表
        tlog.log_info( '查询流程布局表start' )
        sql_lcbj = """select id, x, y, jddyid, jdlx, ssjyid
        from gl_lcbj
        where ssjyid = '%s'
        order by id""" % id
        cur.execute( sql_lcbj )
        rs_lcbj = cur.fetchall()
        tlog.log_info( '查询流程布局表end' )
        # 查询流程走向表
        tlog.log_info( '查询流程走向表start' )
        sql_lczx = """select id, qzjdlcbjid, hzjdlcbjid, fhz, ssid
        from gl_lczx
        where ssid = '%s'
        order by id""" % id
        cur.execute( sql_lczx )
        rs_lczx = cur.fetchall()
        tlog.log_info( '查询流程走向表end' )
        # 计算md5值
        md5 = cal_md5((rs_jydy, rs_lcbj, rs_lczx))
        # 更新唯一码字段值
        sql_data = {'tablename': 'gl_jydy', 'id': id, 'wym': md5}
        sql_update_wym_by_tb = """update %(tablename)s set wym = '%(wym)s'
        where id = '%(id)s'""" % ( sql_data )
        cur.execute( sql_update_wym_by_tb )
    tlog.log_info( '更新交易完成' )



