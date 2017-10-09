# -*- coding: utf-8 -*-
"""  
    定时任务处理
    1.轮询数据库当日计划任务表，检索当天计划发起时间是现在或之前的动作类型非“手工发起”的还未执行的任务；
    2.校验任务是否可并发，可并发的不做处理
      若任务不可并发的：查询响应主机上同类的任务是否正在执行；若有正在执行的，将此任务直接更新成“发起失败”；
    3.检验查询出来的数据中是否有同一主机同一任务，若有执行计划发起时间最晚的一条，其他的任务直接更新状态为：发起失败；
    4.将需要执行的计划任务状态全部更新为：中间状态 9 
    5.循环将计划任务发送到响应动作消息队列（无需反馈值）。
    6.sleep 10秒，再次进行下次循环
"""
import datetime
import cpos.esb.basic.resource.rdb
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.resource.functools import get_hostname
from cpos.esb.basic.busimodel.transutils import get_xtcs


def get_rw():
    """
       # 获取任务表中未发起的任务
    """
    logger.ods( '获取待执行的任务',lv = 'dev',cat = 'app.js')
    now = datetime.datetime.now()
    rq = now.strftime('%Y%m%d')
    sj = now.strftime('%H%M%S')
    sjfqsj = now.strftime('%Y%m%d%H%M%S')
    # 默认的处理jr的主机，在没有配置hostname时使用，目前只有jy类没有配置hostname
    hostname_default = get_hostname()
    # 待执行任务id列表
    rw_rs = []
    with connection() as con:
        # 发起失败任务列表
        rw_rs_false = []
        # 发起成功任务列表
        rw_rs_true = []
        # 不可并发任务ssid列表
        nobf_ssid_lst = [] 
        # dzlx: 2 手工发起  zt： 0 未发起 jhfqsj： hhmmss   sfkbf: 0否， 1：是( 空默认为0 )
        # for update 是为了锁表，在connection结束时释放，这是oracle的语法
        # order by jhfqsj desc 是为了保证使用最新的任务
        sql = """
            select id, ip, case when sfkbf is not null then sfkbf else '0' end as sfkbf, ssid ,rwlx from gl_drzxjhb 
            where rq = %(rq)s and jhfqsj < %(sj)s and ( dzlx !='2' or  dzlx is null )and zt = '0' and id is not null
                order by jhfqsj desc 
            """
        logger.ods( '查询任务的sql为：%s'%sql,lv = 'dev',cat = 'app.js')
        d =  dict( rq=rq, sj=sj )
        rs = con.execute_sql( sql, d )
        logger.ods( '获取到的待执行任务列表长度：%s'%len(rs),lv = 'info',cat = 'app.js')

        # 校验任务是否可并发，可并发的不做处理
        # 不可并发的：1.若是同类上一个任务正在执行，此任务直接更新成“发起失败”
        #            2.获取的结果rs中同类型的只执行时间最晚的一条，之前全部更新成“发起失败”
        for rw in rs:
            id, hostname, sfkbf, ssid ,rwlx = rw['id'] ,rw['ip'] ,rw['sfkbf'] ,rw['ssid'] ,rw['rwlx']
            if not rwlx:
                # 没有任务类型，直接登记失败
                rw_rs_false.append(id)
                continue
            if not hostname:
                logger.ods( '任务【ssid：%s，id：%s，hostname：%s】修改hostname值：%s'%(ssid,id,hostname,hostname_default),lv = 'dev',cat = 'app.js')
                hostname = hostname_default
            # 0: 不可并发
            if sfkbf == '0':
                if ssid in nobf_ssid_lst:
                    # 登记的目的是为了保证本次查询出来的任务中只执行同类的最后一条任务
                    logger.ods( '任务【ssid：%s，id：%s，hostname：%s】失败，非最新任务，不可并发'%(ssid,id,hostname),lv = 'dev',cat = 'app.js')
                    rw_rs_false.append(id)
                    continue
                nobf_ssid_lst.append( ssid )
                # 校验此类任务是否有正在执行的
                sql = """
                    select * from gl_drzxjhb 
                    where rq = %(rq)s and ip = %(ip)s and ssid = %(ssid)s and ( dzlx !='2' or  dzlx is null ) and zt = '9'
                        and sjfqsj < %(sjfqsj)s
                    """
                d = dict( rq=rq, ip=hostname, ssid=ssid ,sjfqsj=sjfqsj )
                run_rw = con.execute_sql( sql, d )
                if len(run_rw) > 0:
                    logger.ods( '任务【ssid：%s，id：%s，hostname：%s】失败，当前有任务正在执行，不可并发'%(ssid,id,hostname),lv = 'dev',cat = 'app.js')
                    rw_rs_false.append(id)
                    continue
            # 不可并发的任务，没有其他在执行的任务，也可以加任务
            # sfkbf 为'1' 可并发，可以直接加任务
            logger.ods( '任务【rwlx：%s，ssid：%s，id：%s，hostname：%s】将被加入到任务列表'%(rwlx,ssid,id,hostname),lv = 'dev',cat = 'app.js')
            rw_rs.append( [rwlx ,id, hostname] ) 
            rw_rs_true.append(id)
        
        # 将失败类的任务更新状态（90：不支持并发，未发起）
        logger.ods( '本次发起失败的数量为：%s'%len(rw_rs_false),lv = 'info',cat = 'app.js')
        for id in rw_rs_false:
            sql_upd = " update gl_drzxjhb set zt = '90' where id = %(id)s "
            d = dict(id=id)
            con.execute_sql( sql_upd, d )
        
        # 将成功类的任务更新状态
        logger.ods( '本次发起成功的数量为：%s'%len(rw_rs_true),lv = 'info',cat = 'app.js')
        for id in rw_rs_true:
            sql_upd = " update gl_drzxjhb set zt = '9',sjfqsj = %(sjfqsj)s where id = %(id)s "
            d = dict(sjfqsj=sjfqsj ,id=id)
            con.execute_sql( sql_upd, d )
    return rw_rs


def get_interval():
    """
        获得数据库轮询的间隔时间
    """
    try:
        return int(get_xtcs("INTERVAL_JS" ,'10'))
    except:
        return 10

if __name__ == '__main__':
    print(get_rw())
