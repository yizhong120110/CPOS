# -*- coding: utf-8 -*-
""" 
    rwlx：fx    数据分析任务
    处理完成后，要根据结果进行后续操作
    csdict 结构示例
    { 'hxdz_dic': {
            'False': [],
            'True': [
                {
                    'dzlx': '1',
                    'sfkbf': 1,
                    'ssid': '5ee165c96cc54d23a445ae76756f747e',
                    'jhfqsj': '1558',
                    'zt': '0',
                    'ip': 'tsgl',
                    'rq': '20150718',
                    'rwlx': 'dz'
                }
            ]
        },
        'funcparam': {
            'ywbm': 'JNGTZY'
        },
        'funcuuid': 'b0232d0edd1f41fb82842e04c376dd47'
    }

"""
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.resource.cache import get_memclient
from cpos.esb.basic.busimodel.cachedobject import GlobalFunction
from cpos.esb.basic.busimodel.dynamicruntime import CommonRuntime
from cpos.esb.app.jr.db_jr import get_xx ,upd_rwxx ,insert_drzxjhrw
from cpos.esb.basic.busimodel.dictlog import tlog ,set_tlog_parms


def main(received_data):
    rzlsh = ""
    memclient = None
    rwid = None
    try:
        rzlsh = set_tlog_parms(tlog ,"jr_fx" ,kind="jr_fx" ,reload_jyzd="yes")
        rwid = received_data.get('rwid','') 
        if not rwid:
            logger.ods( '任务id为空，无需执行',lv = 'dev',cat = 'app.jr_fx')
            tlog.log_info("任务id为空，无需执行")
            return None
        
        # 根据rwid获取与任务有关的所有信息,数据格式： 
        # ["fx"，{'hxdz_dic': {'False': [], 'True': []}, 'funcparam': {'ywbm': 'JNGTZY'}, 'funcuuid': 'b0232d0edd1f41fb82842e04c376dd47'}]
        rwlx ,csdict = get_xx( rwid )
        if not csdict:
            logger.ods( '未获取到任务信息，异常结束！',lv = 'dev',cat = 'app.jr_fx')
            tlog.log_info("未获取到任务信息，异常结束！")
            return None

        memclient = get_memclient()
        # 获得缓存对象
        cmd = GlobalFunction( csdict["funcuuid"] )
        # 进行函数绑定，方便调用
        dr = CommonRuntime()
        dr.np["tlog"] = tlog
        rs_func = dr.call(cmd)
        # 得到调用结果
        fxgzjg = rs_func( **csdict["funcparam"] )
        fxgzjg = str(fxgzjg)
        logger.ods( '任务完成，rwid: %s ,fxgzjg: %s'%(rwid ,fxgzjg),lv = 'info',cat = 'app.jr_fx')
        tlog.log_info( '任务完成，rwid: %s ,fxgzjg: %s'%(rwid ,fxgzjg) )
        
        # 根据类函数不同的返回值更新任务的执行状态 1：发起失败 2：发起成功 
        upd_rwxx( rwid, '2', fxgzjg=fxgzjg ,rzlsh=rzlsh )

        # 获取新任务信息, 数据结构 [{'dzlx': '1', 'sfkbf': 1, 'ssid': '5ee165c96cc54d23a445ae76756f747e', 'jhfqsj': '1558', 'zt':'0', 'ip': 'tsgl', 'rq': '20150718', 'rwlx': 'dz'}]
        # 将新任务增加到定时任务表中
        newJosbs = csdict['hxdz_dic'].get(fxgzjg,[])
        if newJosbs:
            insert_drzxjhrw(newJosbs)
        logger.ods( '数据分析任务完成!',lv = 'dev',cat = 'app.jr_fx')
        tlog.log_info( '数据分析任务完成!' )

        return None
    except:
        if rwid:
            # 若有任务id,更新任务表中的状态
            upd_rwxx( rwid, '1' ,rzlsh=rzlsh)
        logger.oes( '任务执行过程中异常',lv = 'error',cat = 'app.jr_fx')
        tlog.log_exception( "任务执行过程中异常" )
        return None
    finally:
        if rzlsh:
            tlog.close(rzlsh)
        if memclient:
            memclient.disconnect_all()
            logger.ods( "关闭memclient" ,lv = 'dev',cat = 'app.jr_fx')


if __name__=="__main__":
    main({"rwid":"1a997f9b27af406ba56537a24abcfa06"})
