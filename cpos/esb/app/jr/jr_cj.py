# -*- coding: utf-8 -*-
"""
    rwlx：cj    信息采集，函数来自py文件
"""
from cpos.esb.basic.resource.logger import logger
from cpos.esb.app.jr.db_jr import get_xx ,upd_rwxx
from cpos.esb.basic.config import settings
from cpos.esb.basic.resource.dycall import dcallpy ,scall
from cpos.esb.basic.busimodel.dictlog import tlog ,set_tlog_parms
import os


def done_func(parmsdic):
    # 初始化环境
    filename = settings.TRANS_ENV_INIT
    dr = dcallpy(os.path.split(filename)[-1] ,root=os.path.dirname(filename))
    # 加载代码文件
    filename = settings.ZH_MANAGE_PY
    dr = dcallpy(os.path.split(filename)[-1] ,root=os.path.dirname(filename),runtime = dr)
    
    dr.np["parmsdic"] = parmsdic
    dr.np["tlog"] = tlog
    
    func_str = "%s(**parmsdic['classparam']).%s(**parmsdic['funcparam'])"%( parmsdic['classname'].split("(")[0] ,parmsdic['funcname'].split("(")[0] )
    logger.ods ("被调用的函数串为：%s"%(func_str) ,lv='info',cat = 'app.jr_cj')
    tlog.log_info( "被调用的函数串为：%s"%(func_str) )
    # 调用函数
    dr = scall(func_str,runtime = dr)


def main(received_data):
    rzlsh = ""
    rwid = None
    try:
        rzlsh = set_tlog_parms(tlog ,"jr_cj" ,kind="jr_cj" ,reload_jyzd="yes")
        rwid = received_data.get('rwid','') 
        if not rwid:
            logger.ods( '任务id为空，无需执行',lv = 'dev',cat = 'app.jr_cj')
            tlog.log_info("任务id为空，无需执行")
            return None
        
        # 根据rwid获取与任务有关的所有信息,数据格式： 
        # ["dz"，{'funcparam': {'cmd': 'pwd'}, 'funcuuid': '5d0b104fdd534839aba23d7be367184b'}]
        rwlx ,csdict = get_xx( rwid )
        if not csdict:
            logger.ods( '未获取到任务信息，异常结束！',lv = 'dev',cat = 'app.jr_cj')
            tlog.log_info("未获取到任务信息，异常结束！")
            return None
        
        done_func(csdict)
        logger.ods( '任务完成，rwid: %s'%(rwid),lv = 'info',cat = 'app.jr_cj')
        tlog.log_info( '任务完成，rwid: %s'%(rwid) )

        # 根据类函数不同的返回值更新任务的执行状态 1：发起失败 2：发起成功 
        upd_rwxx( rwid, '2' ,rzlsh=rzlsh )
        return None
    except:
        if rwid:
            # 若有任务id,更新任务表中的状态
            upd_rwxx( rwid, '1' ,rzlsh=rzlsh)
        logger.oes( '任务执行过程中异常',lv = 'error',cat = 'app.jr_cj')
        tlog.log_exception( "任务执行过程中异常" )
        return None
    finally:
        if rzlsh:
            tlog.close(rzlsh)


if __name__=="__main__":
    main({"rwid":"ba74fae6915a41118d4e5b2255e47071"})
