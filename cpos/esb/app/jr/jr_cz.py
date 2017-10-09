# -*- coding: utf-8 -*-
"""
    ylsh 要做冲正的原流水号
        6.后台轮循 jy_cz 表，有满足条件数据，则到 JY_HTRZ 查询对应的回退日志列表：
            1.如果jy_cz.czwz 为0，则取回退日志列表中序号最大的信息开始冲正(冲正序号需要大于0)
            2.如果jy_cz.czwz 大于0，则取此位置的信息开始冲正
        7.冲正时，将 jy_htrz.htxx 放到jyzd中，调用jy_htrz.htjd 子流程
        8.jy_ls.zt:
            01:交易成功
            10:交易失败
            88:交易执行异常
            90:冲正中
            98:冲正失败
            99:被冲正
            操作时，需要更新
    由于在执行ZLC的调用时，将czlsh作为SYS_XTLSH赋值在jyzd中，会使upd_lsh提示lsh更新失败，这是正常现象，因为没有insert该lsh到jy_ls中
    处理中校验的内容
        ◆原流水号不能为空
        ◆jy_cz.rq=time.strftime('%Y%m%d')
        ◆jy_cz.zt='1'
        ◆jy_cz.czwz的值表明有可冲正的节点或尚未冲正：jy_cz.czwz > jy_htrz.xh or jy_cz.czwz = '0'
        ◆对于jy_ls表：
            不能处理找不到记录的数据，且不能处理交易成功、被冲正的数据
            冲正中的不能再次冲正
            jy_ls.zt in ("10","88","98") or (jy_ls.zt=='90' and 更新前的交易状态!='90')
    # 测试时，需要指定jyrq='20151020'
    print(main({"ylsh":"999906",'czlsh':'19111'}))
"""
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.busimodel.dictlog import tlog ,set_tlog_parms
from cpos.esb.basic.resource.cache import get_memclient
from cpos.esb.app.jr.db_jr_cz import upd_jycz ,upd_jycz_flag ,upd_jyls ,upd_jyls_flag ,get_czxx
import cpos.esb.basic.rpc.rpc_transaction as rtrans
import time


def main(received_data):
    rzlsh = ""
    memclient = None
    # 交易日期
    jyrq = time.strftime('%Y%m%d')
    ylsh = received_data.get('ylsh','') 
    # 这里赋值是为了在异常时，如果没有走到yclcs的赋值部分，也能够修改状态，用于提示人工处理
    yclcs = 3
    ylshzt = '98'
    try:
        # 使用传入的czlsh作为rzlsh，目的是将冲正日志放到一起展示
        czlsh = received_data.get('czlsh','')
        rzlsh = set_tlog_parms(tlog ,"jr_cz" ,filename=czlsh or None ,kind="jr_cz" ,reload_jyzd="yes")
        if not ylsh:
            logger.ods( 'ylsh为空，无需执行冲正操作',lv = 'dev',cat = 'app.jr_cz')
            tlog.log_info("ylsh为空，无需执行冲正操作")
            return None

        # 根据ylsh获取与任务有关的所有信息,数据格式： 
        # 0 ,[{'xh': 1, 'htxx': '', 'cllx': 'ZLC', 'htcluuid': '5d0b104fdd534839aba23d7be367184b'},{'xh': 2, 'htxx': '', 'cllx': 'ZLC', 'htcluuid '5d0b104fdd534839aba23d7be367184b'}]
        # 获得冲正使用的信息
        yclcs ,htxxlist = get_czxx( jyrq ,ylsh )
        tlog.log_info( "查询到的回退列表: %s"%str(htxxlist) )
        # yclcs 用于冲正执行结束时，登记 jy_cz 表
        if not htxxlist:
            logger.ods( '未获取到任务信息，异常结束！原流水号: %s %s'%(jyrq ,ylsh),lv = 'dev',cat = 'app.jr_cz')
            tlog.log_info("未获取到任务信息，异常结束！原流水号: %s %s"%(jyrq ,ylsh))
            return None

        # 记录冲正流水号 ,再次更新zt是为了复用代码
        upd_jycz( jyrq, ylsh , '1' ,czlsh=str(rzlsh) )

        logger.ods( '将要执行冲正操作，原流水号: %s %s ，待冲正节点数量：%s'%(jyrq ,ylsh,len(htxxlist)),lv = 'dev',cat = 'app.jr_cz')
        tlog.log_info( '将要执行冲正操作，原流水号: %s %s ，待冲正节点数量：%s'%(jyrq ,ylsh,len(htxxlist)) )
        
        # 先更新原交易流水的状态为“冲正中”
        flag ,ylshzt = upd_jyls( jyrq, ylsh , '90' )
        if flag == False:
            # 更新原交易流水状态失败，停止处理，增加冲正次数，改变冲正状态
            logger.ods( '更新原交易流水状态失败，冲正失败！',lv = 'dev',cat = 'app.jr_cz')
            tlog.log_info( '更新原交易流水状态失败，冲正失败！' )
            upd_jycz_flag(jyrq, ylsh ,False ,yclcs)
            return None
        logger.ods( '更新原交易流水状态成功，被冲正交易原状态为：%s'%(ylshzt),lv = 'dev',cat = 'app.jr_cz')
        tlog.log_info( '更新原交易流水状态成功，被冲正交易原状态为：%s'%(ylshzt) )

        memclient = get_memclient()
        sys_jyjdgz_his = ''
        for czxxdict in htxxlist:
            if czxxdict["cllx"] == "ZLC":
                jyzd = eval(czxxdict["htxx"])
                jyzd.update({'SYS_ISDEV':'yes' ,'SYS_JYLX':'02' ,'SYS_CLBZ':'02','SYS_CSSJ':50 ,'ISSAF':'no' ,
                    # 用于更新jy_ls中冲正交易的相关字段
                    'SYS_YJYRQ':jyrq ,'SYS_YLSH':ylsh ,'SYS_JYJDGZ_HIS':sys_jyjdgz_his,'msgxh':str(tlog.d.msgxh),
                    # 共用一个流水号，为了能够将日志放到一起展示
                    'SYS_XTLSH':str(rzlsh) or None ,
                    'SYS_DZXJDDM':czxxdict["htcluuid"],'SYS_ZLCBM':czxxdict["htclbm"], 'SYS_JYM':czxxdict["jym"]
                    })
                try:
                    jyzd = rtrans.send_trans_with_protocol(jyzd,timeout_interval=60, try_once=True)
                except:
                    jyzd = None
                    logger.ods( '冲正操作处理异常，冲正失败',lv = 'dev',cat = 'app.jr_cz')
                    tlog.log_info( '冲正操作处理异常，冲正失败' )
                
                tlog.d.msgxh = str(jyzd.get('msgxh' ,tlog.d.msgxh)) 
                logger.ods( '单节点冲正完成 节点序号：%s'%(czxxdict["xh"]),lv = 'dev',cat = 'app.jr_cz')
                tlog.log_info( '单节点冲正完成 节点序号：%s，执行结果为：%s'%(czxxdict["xh"],str(jyzd)) )
                # 需要根据冲正节点的结果，做后续处理，决定是否继续冲正，或者直接跳出循环
                if jyzd is not None and jyzd.get("SYS_RspCode",None)=="000000":
                    # 更新冲正信息表中的冲正节点
                    upd_jycz(jyrq, ylsh , '1', czwz=czxxdict["xh"])
                    tlog.log_info( "单节点处理成功，更新状态，xh：%s"%(czxxdict["xh"]) )
                    sys_jyjdgz_his += jyzd["SYS_JYJDGZ"]
                else:
                    # 冲正失败，更新状态
                    upd_jycz_flag(jyrq, ylsh ,False ,yclcs)
                    # 更新原交易流水的状态
                    upd_jyls_flag(jyrq, ylsh ,False ,yclcs ,ylshzt)
                    tlog.log_info( "单节点处理失败，停止冲正" )
                    return None

        # 更新冲正完成后的结果
        upd_jycz_flag(jyrq, ylsh ,True ,yclcs)
        # 更新原交易流水的状态为“冲正成功”
        upd_jyls_flag(jyrq, ylsh ,True ,yclcs ,ylshzt)
        tlog.log_info( "冲正成功结束" )
    except:
        logger.oes( '任务执行过程中异常',lv = 'error',cat = 'app.jr_cz')
        tlog.log_exception( "任务执行过程中异常" )
        try:
            if ylsh:
                # 冲正失败，更新状态
                upd_jycz_flag(jyrq, ylsh ,False ,yclcs)
                # 更新原交易流水的状态
                upd_jyls_flag(jyrq, ylsh ,False ,yclcs ,ylshzt)
                tlog.log_info( "except中更新状态成功" )
        except:
            tlog.log_info( "except中更新状态失败" )
    finally:
        if rzlsh:
            tlog.close(rzlsh)
        if memclient:
            memclient.disconnect_all()
            logger.ods( "关闭memclient" ,lv = 'dev',cat = 'app.jr_cz')
    return None


if __name__=="__main__":
    # 测试时，需要指定jyrq='20151020'
    print(main({"ylsh":"999906" ,'czlsh':'19985'}))
#    dz shell带参数：c86f8519c4d548b5a3a452f6b4227585
#    dz shell不带参数：7409228d2a2f4968ba000908b5b9b56a
#    rwlx ,csdict = get_xx( "c86f8519c4d548b5a3a452f6b4227585" )
#    callobj = Sbin_CachedObject( csdict["funcuuid"] )
#    print(callobj.run(csdict["funcparam"]))
#    rwlx ,csdict = get_xx( "7409228d2a2f4968ba000908b5b9b56a" )
#    callobj = Sbin_CachedObject( csdict["funcuuid"] )
#    print(callobj.run(csdict["funcparam"]))
