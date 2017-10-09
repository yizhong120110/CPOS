# -*- coding: utf-8 -*-
"""
    rwlx：dz，执行动作，函数来自memcache
"""
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.busimodel.cachedobject import GlobalFunction ,Sbin_CachedObject
from cpos.esb.basic.busimodel.dynamicruntime import CommonRuntime
from cpos.esb.app.jr.db_jr import get_xx ,upd_rwxx
from cpos.esb.basic.busimodel.dictlog import tlog ,set_tlog_parms
from cpos.esb.basic.application.app_ctrle_startpy import shellcall_args
from cpos.esb.basic.resource.cache import get_memclient
from cpos.esb.basic.config import settings
import os
import datetime


def main(received_data):
    rzlsh = ""
    memclient = None
    rwid = None
    try:
        rzlsh = set_tlog_parms(tlog ,"jr_dz" ,kind="jr_dz" ,reload_jyzd="yes")
        rwid = received_data.get('rwid','') 
        if not rwid:
            logger.ods( '任务id为空，无需执行',lv = 'dev',cat = 'app.jr_dz')
            tlog.log_info("任务id为空，无需执行")
            return None
        
        # 根据rwid获取与任务有关的所有信息,数据格式： 
        # ["dz"，{'funcparam': {'cmd': 'pwd'}, 'funcuuid': '5d0b104fdd534839aba23d7be367184b'}]
        rwlx ,csdict = get_xx( rwid )
        if not csdict:
            logger.ods( '未获取到任务信息，异常结束！',lv = 'dev',cat = 'app.jr_dz')
            tlog.log_info("未获取到任务信息，异常结束！")
            return None

        logger.ods( '将要执行任务，rwid: %s  memcache_Lx:%s'%(rwid ,csdict['lx']),lv = 'info',cat = 'app.jr_dz')
        tlog.log_info( '将要执行任务，rwid: %s  memcache_Lx:%s'%(rwid ,csdict['lx']) )

        memclient = get_memclient()
        if csdict["lx"] == "HS":
            # 获得缓存对象
            cmd = GlobalFunction( csdict["funcuuid"] ,memclient )
            # 进行函数绑定，方便调用
            dr = CommonRuntime()
            dr.np["tlog"] = tlog
            rs_func = dr.call(cmd)
            # 得到调用结果
            rs_func( **csdict["funcparam"] )

        elif csdict["lx"] == "HS_SHELL":
            callobj = Sbin_CachedObject( csdict["funcuuid"] ,memclient )
            rsdic = callobj.run(csdict["funcparam"])
            
            filename = "%s_%s.sh"%(datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f') ,rsdic['filename'])
            full_path = os.path.abspath(os.path.join(settings.SBINPATH, filename))
            logger.ods( '待执行代码保存位置为：'+str(full_path) ,lv = 'info',cat = 'app.jr_dz')
            tlog.log_info( '待执行代码保存位置为：'+str(filename) )

            os.makedirs(os.path.dirname(full_path) , exist_ok = True)
            file_object = open(full_path, 'w')
            file_object.write(rsdic['dm'])
            file_object.close()
            
            rsflag ,rsmsg = shellcall_args(["sh" ,full_path]+list(rsdic['params']) ,isrsmsg=True)
            tlog.log_info( '执行结果为，%s: %s'%(rsflag ,rsmsg) )


        logger.ods( '任务完成，rwid: %s'%(rwid),lv = 'info',cat = 'app.jr_dz')
        tlog.log_info( '任务完成，rwid: %s'%(rwid) )

        # 根据类函数不同的返回值更新任务的执行状态 1：发起失败 2：发起成功 
        upd_rwxx( rwid, '2' ,rzlsh=rzlsh )
        return None
    except:
        if rwid:
            # 若有任务id,更新任务表中的状态
            upd_rwxx( rwid, '1' ,rzlsh=rzlsh)
        logger.oes( '任务执行过程中异常',lv = 'error',cat = 'app.jr_dz')
        tlog.log_exception( "任务执行过程中异常" )
        return None
    finally:
        if rzlsh:
            tlog.close(rzlsh)
        if memclient:
            memclient.disconnect_all()
            logger.ods( "关闭memclient" ,lv = 'dev',cat = 'app.jr_dz')


if __name__=="__main__":
    main({"rwid":"7409228d2a2f4968ba000908b5b9b56a"})
#    dz shell带参数：c86f8519c4d548b5a3a452f6b4227585
#    dz shell不带参数：7409228d2a2f4968ba000908b5b9b56a
#    rwlx ,csdict = get_xx( "c86f8519c4d548b5a3a452f6b4227585" )
#    callobj = Sbin_CachedObject( csdict["funcuuid"] )
#    print(callobj.run(csdict["funcparam"]))
#    rwlx ,csdict = get_xx( "7409228d2a2f4968ba000908b5b9b56a" )
#    callobj = Sbin_CachedObject( csdict["funcuuid"] )
#    print(callobj.run(csdict["funcparam"]))
