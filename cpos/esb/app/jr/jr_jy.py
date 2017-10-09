# -*- coding: utf-8 -*-
""" 
    定时交易处理函数
"""
from cpos.esb.basic.resource.logger import logger
from cpos.esb.app.jr.db_jr import get_xx ,upd_rwxx
from cpos.esb.basic.icm.icm_network import send_to_icm_noreply_2 as send_to_icm_noreply
from cpos.esb.basic.busimodel.dictlog import tlog ,set_tlog_parms
import time


def main(received_data):
    rzlsh = ""
    rwid = None
    try:
        rzlsh = set_tlog_parms(tlog ,"jr_jy" ,kind="jr_jy" ,reload_jyzd="yes")
        rwid = received_data.get('rwid','') 
        if not rwid:
            logger.ods( '任务id为空，无需执行',lv = 'dev',cat = 'app.jr_jy')
            tlog.log_info("任务id为空，无需执行")
            return None
        
        # 1.根据rwid获取与定时任务有关的所有信息,数据格式： [任务执行种类，{'任务种类'：[]}]
        rwlx ,csdict = get_xx( rwid )
        if not csdict:
            logger.ods( '未获取到任务信息，异常结束！',lv = 'dev',cat = 'app.jr_jy')
            tlog.log_info("未获取到任务信息，异常结束！")
            return None
        
        # 自动发起交易的通讯节点代码
        commid = str(csdict['commid'])
        logger.ods( '进程命令执行，参数为【%s,%s】'%(str(commid),str(csdict['buf'])),lv = 'info',cat = 'app.jr_jy')
        tlog.log_info( '进程命令执行，参数为【%s,%s】'%(str(commid),str(csdict['buf'])) )
        errcount = 0
        while True:
            try:
                send_to_icm_noreply(commid,csdict['buf'])
                break
            except:
                errcount += 1
                logger.oes ("send_to_icm_noreply failed.[%s]"%(errcount) ,lv='error',cat = 'app.jr_jy')
                time.sleep(1)
                if errcount > 3:
                    errmsg = "send_to_icm_noreply except count is %s, not try again."%(errcount)
                    logger.ods (errmsg ,lv='info',cat = 'app.jr_jy')
                    raise RuntimeError(errmsg)
        tlog.log_info("send_to_icm_noreply调用完成")
        
        # 3.根据类函数不同的返回值更新任务的执行状态 1：发起失败 2：发起成功 
        upd_rwxx( rwid, '2' ,rzlsh=rzlsh )
        return None  
    except :
        if rwid:
            # 若有任务id,更新任务表中的状态为失败
            upd_rwxx( rwid, '1' ,rzlsh=rzlsh)
        logger.oes( '任务执行过程中异常',lv = 'error',cat = 'app.jr_jy')
        tlog.log_exception( "执行出现异常" )
        return None
    finally:
        if rzlsh:
            tlog.close(rzlsh)

