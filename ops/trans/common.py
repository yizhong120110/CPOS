# -*- coding: utf-8 -*-
""" 公共函数 """

import datetime, traceback, pickle, json
from ops.core.utils import get_uuid
from ops.core.rdb_jr import insert_drzxjhrw


def get_zdfssvr_buf(jym ,jsonloads):
    """
        构建 ZDFSSVR 使用的报文
        jsonloads : 将使用json.dumps处理的内容
    """
    buf = jym + ' '*(16 - len(jym)) + json.dumps( jsonloads )
    buf = '%04d'%(len(buf)+4) + buf
    return buf.encode('utf8')


def pl_z_db( jym, xx_lst, txglbm = '' ,buffnc = get_zdfssvr_buf, sfkbf = '0' ):
    """
    # 自动处理批量转单笔
    # 参数：
        jym：批量发起交易码
        xx_lst：批量发起信息列[[报文，距离当前时间多少秒后执行],[报文，距离当前时间多少秒后执行]]
        txglbm：发起通讯编码（ 默认为：自动发起交易svr端：ZDFSSVR ）
        buffnc：报文组织回调函数，用于生成报文，需要输入两个参数
            参数1：交易码
            参数2：交易使用的变量
            返回值：报文串，bytes类型
        sfkbf: 是否可并发( 只对任务类型是分析和采集的有用，0：否，1：是 )
    """
    try:
        with connection() as db:
#            # 首先获取本交易对应的计划任务信息
#            sql_jhrwb = """ select id from gl_jhrwb where ssid in (
#                      select id from gl_jydy where jym = '%s') """ % ( jym )
#            rs_jhrwb = db.execute_sql( sql_jhrwb )
#            if not rs_jhrwb:
#                return False, '交易[%s]未定义交易自动发起配置，无法实现批量转单笔' % jym
            
            # 根据jym获取交易信息
            sql_jyxx = "select id from gl_jydy where jym = '%s'" % ( jym )
            rs_jyxx = db.execute_sql( sql_jyxx )
            if not rs_jyxx:
                return False, '交易[%s]未被定义，无法实现批量转单笔' % jym
            
            # 整理向当日执行计划任务表中插入的数据列表
            ## 首先先获取当前时间
            now_date = datetime.datetime.today()
            now_rq = now_date.strftime( '%Y%m%d' )
            ## 循环报文和发起时间戳，组织当日执行计划任务表 数据
            ## 当日执行计划任务表列表
            drzxjhb_lst = []
            ## 批量转单笔表列表
            plzdb_lst = []
            for xx_mx_lst in xx_lst:
                # 当日执行计划任务表id
                drzxjhbid = get_uuid()
                # 发起时间（ 当前日期+时间戳 ）
                jhfqsj = (now_date + datetime.timedelta( seconds = int( xx_mx_lst[1] ))).strftime('%H%M%S')
                # 将信息写入到列表
                drzxjhb_lst.append(
                    { 'id': drzxjhbid, 'rwlx': 'jy', 'ssid': rs_jyxx[0]['id'],
                    'rq': now_rq, 'jhfqsj': jhfqsj, 'zt': '0', 'sfkbf': sfkbf } )
                # 通讯编码或报文存在
                if txglbm or xx_mx_lst[0]:
                    plzdb_lst.append(
                        { 'id': get_uuid(), 'drzxjhbid': drzxjhbid, 
                        'buf': pickle.dumps( buffnc(str(jym) ,xx_mx_lst[0]) ), 'txglbm': txglbm }
                    )
            
            ## 插入批量转单笔表列表
            if plzdb_lst:
                sql_ins = """insert into gl_plzdb( id, drzxjhbid, buf, txglbm )
                            values( %(id)s, %(drzxjhbid)s, %(buf)s, %(txglbm)s )
                    """
                for plzdb_dic in plzdb_lst:
                    db.execute_sql( sql_ins, plzdb_dic )
        ## 插入当日执行计划任务表
        insert_drzxjhrw( drzxjhb_lst )
        
        return True, '批量转单笔展开成功，等待计划任务执行'
    except:
        # 交易批量转单笔失败
        tlog.log_exception( 'pl_z_db 批量转单笔失败：' )
        return False, '交易[%s]批量转单笔出现异常' % jym

#if __name__=="__main__":
#    jym = 'jy1208'
#    xx_lst = [["{'a': 1, 'b': 2}",120],["{'a': 3, 'b': 4}",240],["{'a': 5, 'b': 6}",360]]
#    ret, msg = pl_z_db( jym, xx_lst )
#    print ( 'ret:', ret )
#    print ( 'msg:', msg )

