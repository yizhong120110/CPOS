# -*- coding: utf-8 -*-
from cpos.esb.basic.busimodel.cachedobject import *
from cpos.esb.basic.busimodel.dynamicruntime import *
from cpos.esb.basic.busimodel.transutils import get_xtlsh, ins_lsz, upd_lsz, e_now ,ins_jycz ,is_trans_timeout, get_xtcs, cnt_hyrz
from cpos.esb.basic.substrate.types import StrAttrDict as AttrDict
from cpos.esb.basic.resource.functools import traceback2
from cpos.esb.basic.busimodel.dictlog import tlog ,set_tlog_parms
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.resource.cache import get_memclient
from cpos.esb.basic.config import settings
if settings.DB_TYPE == "postgresql":
    from psycopg2 import IntegrityError as PrimaryKeyError
else:
    from cx_Oracle import IntegrityError as PrimaryKeyError
import datetime


jyjszt_dict = {"000000":"01","TS9999":"88"}

def err_comm(jyzd):
    """
        # 异常时的通用处理操作
        jyzd 必须传入的key：SYS_JYRQ、SYS_XTLSH
    """
    jyzd.SYS_RspCode = "TS9999"
    jyzd.SYS_RspInfo = "交易执行异常"
    jyzd.SYS_CLBZ = '03'
    if not jyzd.SYS_YFSDBW:
        jyzd.SYS_YFSDBW = bytes([])
    if not jyzd.SYS_CSSJ:
        jyzd.SYS_CSSJ = '-1'
    jyjszt = jyjszt_dict.get(jyzd.SYS_RspCode,"10")
    # SYS_JYJDGZ_HIS 是为了能够在冲正的处理时，将SYS_JYJDGZ的值做追加更新
    upd_lsz(jyzd.SYS_JYRQ,int(jyzd.SYS_XTLSH),**{'zt':jyjszt,'xym':jyzd.SYS_RspCode,'xynr':jyzd.SYS_RspInfo[:1000],'jyjssj':e_now(),'jyjdgz':(jyzd.SYS_JYJDGZ_HIS or '')+(jyzd.SYS_JYJDGZ or '')})

def err_rqcl(jyzd):
    """
        # 日切时交易暂停的返回信息
    """
    jyzd.SYS_RspCode = "TS9944"
    jyzd.SYS_RspInfo = "系统日切，交易暂停"
    jyzd.SYS_CLBZ = '03'
    if not jyzd.SYS_YFSDBW:
        jyzd.SYS_YFSDBW = bytes([])
    if not jyzd.SYS_CSSJ:
        jyzd.SYS_CSSJ = '-1'
    jyjszt = jyjszt_dict.get(jyzd.SYS_RspCode,"10")
    # SYS_JYJDGZ_HIS 是为了能够在冲正的处理时，将SYS_JYJDGZ的值做追加更新
    upd_lsz(jyzd.SYS_JYRQ,int(jyzd.SYS_XTLSH),**{'zt':jyjszt,'xym':jyzd.SYS_RspCode,'xynr':jyzd.SYS_RspInfo[:1000],'jyjssj':e_now(),'jyjdgz':(jyzd.SYS_JYJDGZ_HIS or '')+(jyzd.SYS_JYJDGZ or '')})

class RQCLError(RuntimeError):
    """ 日切处理时抛出的异常 """
    pass

def jycl(jyzd):
    """
        # jyzd 的格式应该为dict，如果是json串，应该在传入前做转换
        #    传入字典的数据格式{'SYS_CLBZ':'', 'SYS_JSDDBW':'', 'SYS_TXJBID':''}
        # 返回码说明 UN0001至UN0999为处理成功的返回码；UN1001至UN1999为处理失败的返回码
        # SYS_CLBZ：01 交易识别；02 交易处理；03 交易结束
        # 最开始的字典 {'SYS_CLBZ':'01', 'SYS_JSDDBW':'', 'SYS_TXJBID':''}
        # 最后结束时最简版的字典 {'SYS_CLBZ':'03', 'SYS_JSDDBW':'', 'SYS_TXJBID':'', 'SYS_YFSDBW':bytes([])}
    """
    """
        1.初始化log记录对象tlog
        2.判断处理标志：
           若处理标志为01：交易识别
               调用CommunicationNode类根据SYS_TXJBID从memcache中获取交易码解包函数；
               调用TransactionIdentificationRuntime类中的call函数，执行交易码解包函数，将交易码存放到jyzd中；
               若SYS_JYM为空，交易码没有赋值，结束；若不为空，继续；
               根据SYS_JYM初始化Transaction类对象JY；
               JY对象调用函数get_cssj、get_jymc获取交易超时时间和交易名称，并赋值到jyzd中；
               更新jyzd中SYS_CLBZ字段的值为02；
               初始化交易必要字段：系统流水号、响应码、响应内容；
               向交易流水表中记录一条新交易信息。
           若处理标志为02：交易处理
               根据SYS_JYM初始化Transaction类对象JY；
               调用JY对象get_jyssywdm、get_jyssywmc、get_jycs_all函数获取业务代码、业务名称和交易全局参数，赋值到jyzd中；
               调用FlowDynamicRuntime初始化交易执行环境；
               调用JY对象中的call函数执行交易解包节点；
               调用JY对象get_jyzt获取交易状态，若不为1，则交易为“暂停”状态，结束；若是1，继续执行交易；
               使用 while jycl.next()的方式按顺序执行交易中所有的节点函数

               若出现异常记录，记录失败原因。

               最后在finally中，调用JY对象get_jydb_callable函数获取打包函数，并使用jycl中的call函数执行打包函数，将打包的报文赋值到jyzd中；
               根据响应码得到响应的状态字段值，并更新交易流水表信息。
           返回交易字典。
    """
    memclient = get_memclient()
    if jyzd.SYS_CLBZ == '01':
        try:
            try:
                cnd = CommunicationNode(jyzd.SYS_TXJBID ,memclient)
                logger.ods( "通过SYS_TXJBID获取信息 成功" ,lv = 'dev',cat = 'app.tp')
            except:
                tlog.log_exception("失败：")
                raise RuntimeError("通过SYS_TXJBID获取信息 失败")

            tlog.log_info("交易识别--交易码解出")
            try:
                dr = TransactionIdentificationRuntime(jyzd)
                logger.ods( "交易对象初始化 成功" ,lv = 'dev',cat = 'app.tp')
            except:
                tlog.log_exception("失败：")
                raise RuntimeError("交易对象初始化 失败")
            dr.np['tlog'] = tlog
            dr.call(cnd)

            if not jyzd.SYS_JYM:
                raise RuntimeError("交易码没有赋值")

            try:
                JY = Transaction(jyzd.SYS_JYM ,memclient)
                logger.ods( "通过SYS_JYM获取信息 成功" ,lv = 'dev',cat = 'app.tp')
            except:
                tlog.log_exception("失败：")
                raise RuntimeError("通过SYS_JYM获取信息 失败")

            # 设置超时时间
            tlog.log_info("交易识别--设置SYS参数")
            jyzd.SYS_CSSJ = JY.get_cssj()
            jyzd.SYS_CLBZ = '02'
            jyzd.SYS_JYMC = JY.get_jymc()
            logger.ods( "交易识别--设置SYS参数 成功" ,lv = 'dev',cat = 'app.tp')
            # 登记交易流水表
            ins_lsz( int(jyzd.SYS_XTLSH), jyzd.SYS_JYRQ, jyzd.SYS_JYSJ, jyzd.SYS_JYM )
            tlog.log_info("交易识别--处理结束")
            logger.ods( "交易识别--处理结束" ,lv = 'dev',cat = 'app.tp')

            # 在RMQ上的等待时间过长，已经不再等待返回值
            if is_trans_timeout(jyzd.SYS_RPC_CSSJ ,jyzd.SYS_CTIME):
                raise RuntimeError("交易处理超时，RMQ等待超时")
        except:
            logger.oes( '交易识别出错'+str(jyzd) ,lv = 'error',cat = 'app.tp')
            tlog.log_exception("交易识别出错：")
            # 为jyzd.SYS_RspCode赋值“TS9999”、jyzd.SYS_RspInfo赋值“交易执行异常”
            err_comm(jyzd)

    elif jyzd.SYS_CLBZ == '02':
        try:
            # 交易对象
            try:
                JY = Transaction(jyzd.SYS_JYM ,memclient)
                logger.ods( "通过SYS_JYM获取信息 成功" ,lv = 'dev',cat = 'app.tp')
            except:
                tlog.log_exception("失败：")
                raise RuntimeError("通过SYS_JYM获取信息 失败")

            # 交易的业务代码
            jyzd.SYS_YWDM = JY.get_jyssywdm()
            # 交易的业务名称
            jyzd.SYS_YWMC = JY.get_jyssywmc()

            # jyzd中加载 交易参数
            tlog.log_info("交易处理--jyzd中加载 交易参数")
            jyzd.update(JY.get_jycs_all())
            logger.ods( "交易处理--jyzd中加载 交易参数" ,lv = 'dev',cat = 'app.tp')

            # 初始化执行环境
            tlog.log_info("交易处理--初始化执行环境")
            try:
                jycl = FlowDynamicRuntime(JY.get_jygghs(),JY, jyzd)
                logger.ods( "交易处理--初始化执行环境 成功" ,lv = 'dev',cat = 'app.tp')
            except:
                tlog.log_exception("失败：")
                raise RuntimeError("交易流程初始化 失败")
            jycl.np['tlog'] = tlog

            # 交易解包
            tlog.log_info("交易处理--交易解包")
            jycl.call(JY.get_jyjb_callable())
            logger.ods( "交易处理--交易解包 成功" ,lv = 'dev',cat = 'app.tp')

            # 增加交易解包之后判断jyzd.SYS_RspCode的部分

            if JY.get_jyzt() != '1':
                raise RuntimeError('交易暂停')

            # 系统的级别
            t_xtl = get_xtcs("SYS_XTCLLEVEL" ,"0")
            # 交易的级别
            t_jyl = jyzd.SYS_JYLEVEL or "-1"
            # 当 SYS_JYLEVEL 大于0，且小于SYS_XTCLLEVEL时，交易失败
            if int(t_jyl) >0 and int(t_xtl) > int(t_jyl):
                raise RQCLError("系统级别[%s],交易级别[%s],交易暂停处理"%(t_xtl, t_jyl))

            # 根据响应码判断解包是否成功，若失败不执行交易节点打包返回
            if jyzd.SYS_RspCode == '000000':
                tlog.log_info("交易处理--交易节点代码执行")
                logger.ods( "交易处理--交易节点代码执行" ,lv = 'dev',cat = 'app.tp')
                while jycl.next():
                    logger.ods( "交易处理--待执行节点："+str(jycl.next_name) ,lv = 'dev',cat = 'app.tp')
                tlog.log_info("交易处理--处理结束")
                logger.ods( "交易处理--处理结束" ,lv = 'dev',cat = 'app.tp')
            else:
                tlog.log_info("解包节点执行失败，执行下一个节点打包")
        except RQCLError:
            logger.oes( '系统日切，交易处理失败：' ,lv = 'warning',cat = 'app.tp')
            tlog.log_exception("交易处理失败：")
            # 为jyzd.SYS_RspCode赋值“TS9999”、jyzd.SYS_RspInfo赋值“交易执行异常”
            err_rqcl(jyzd)
        except:
            logger.oes( '交易处理失败：'+str(jyzd) ,lv = 'error',cat = 'app.tp')
            tlog.log_exception("交易处理失败：")
            # 为jyzd.SYS_RspCode赋值“TS9999”、jyzd.SYS_RspInfo赋值“交易执行异常”
            err_comm(jyzd)
        finally:
            tlog.log_info("交易处理--交易打包")
            logger.ods( "交易处理--交易打包" ,lv = 'dev',cat = 'app.tp')
            try:
                # 交易打包
                jycl.call(JY.get_jydb_callable())
                jyzd.SYS_CLBZ = '03'
                logger.ods( "交易处理--交易打包--逻辑处理" ,lv = 'dev',cat = 'app.tp')

                jyjszt = jyjszt_dict.get(jyzd.SYS_RspCode,"10")
                # SYS_JYJDGZ_HIS 是为了能够在冲正的处理时，将SYS_JYJDGZ的值做追加更新
                upd_lsz(jyzd.SYS_JYRQ,int(jyzd.SYS_XTLSH),**{'zt':jyjszt,'xym':jyzd.SYS_RspCode,'xynr':jyzd.SYS_RspInfo[:1000],'jyjssj':e_now(),'jyjdgz':(jyzd.SYS_JYJDGZ_HIS or '')+(jyzd.SYS_JYJDGZ or '')})
                logger.ods( "交易处理--交易打包--数据库操作" ,lv = 'dev',cat = 'app.tp')

                if is_trans_timeout(jyzd.SYS_CSSJ ,jyzd.SYS_CTIME):
                    raise RuntimeError("交易处理超时")
            except:
                logger.oes( '交易处理--交易打包失败：'+str(jyzd) ,lv = 'error',cat = 'app.tp')
                tlog.log_exception("交易处理--交易打包失败：")
                # 为jyzd.SYS_RspCode赋值“TS9999”、jyzd.SYS_RspInfo赋值“交易执行异常”
                err_comm(jyzd)
            # 仅交易处理中增加冲正操作，单步调试不增加冲正
            try:
                if jyzd.SYS_RspCode != '000000' and jyzd.ISSAF == "yes":
                    ins_jycz( int(jyzd.SYS_XTLSH), jyzd.SYS_JYRQ, cs = int(jyzd.SYS_CZ_CS or 0) )
                logger.ods( "交易处理--登记冲正信息" ,lv = 'dev',cat = 'app.tp')
            except:
                logger.oes( '交易处理--登记冲正信息 失败：'+str(jyzd) ,lv = 'error',cat = 'app.tp')
    if memclient:
        memclient.disconnect_all()
        logger.ods( "关闭memclient" ,lv = 'dev',cat = 'app.tp')
    return jyzd


def jycl_dev(jyzd):
    memclient = get_memclient()
    if jyzd.SYS_CLBZ == '01':
        try:
            try:
                cnd = CommunicationNode(jyzd.SYS_TXJBID ,memclient)
                logger.ods( "dev：通过SYS_TXJBID获取信息 成功" ,lv = 'dev',cat = 'app.tp')
            except:
                tlog.log_exception("失败：")
                raise RuntimeError("dev：通过SYS_TXJBID获取信息 失败")

            tlog.log_info("dev：交易识别--交易码解出")

            try:
                dr = TransactionIdentificationRuntime(jyzd)
                logger.ods( "dev：交易对象初始化 成功" ,lv = 'dev',cat = 'app.tp')
            except:
                tlog.log_exception("失败：")
                raise RuntimeError("dev：交易对象初始化 失败")

            dr.np['tlog'] = tlog
            dr.call(cnd)

            if not jyzd.SYS_JYM:
                raise RuntimeError("dev：交易码没有赋值")
            logger.ods( "dev：交易码赋值 成功" ,lv = 'dev',cat = 'app.tp')

            try:
                JY = Transaction(jyzd.SYS_JYM ,memclient)
                logger.ods( "dev：通过SYS_JYM获取信息 成功" ,lv = 'dev',cat = 'app.tp')
            except:
                tlog.log_exception("失败：")
                raise RuntimeError("dev：通过SYS_JYM获取信息 失败")

            # 设置超时时间
            tlog.log_info("dev：交易识别--设置超时时间")
            jyzd.SYS_CSSJ = JY.get_cssj()
            logger.ods( "dev：交易识别--设置超时时间 成功" ,lv = 'dev',cat = 'app.tp')

            # 登记交易流水表
            ins_lsz( int(jyzd.SYS_XTLSH), jyzd.SYS_JYRQ, jyzd.SYS_JYSJ, jyzd.SYS_JYM )
            jyzd.SYS_CLBZ = '03'
            tlog.log_info("dev：交易识别--处理结束")
            logger.ods( "dev：交易识别--处理结束 成功" ,lv = 'dev',cat = 'app.tp')
        except:
            logger.oes( 'dev：交易识别--处理失败：'+str(jyzd) ,lv = 'error',cat = 'app.tp')
            tlog.log_exception("dev：交易识别--处理失败：")
            # 为jyzd.SYS_RspCode赋值“TS9999”、jyzd.SYS_RspInfo赋值“交易执行异常”
            err_comm(jyzd)

    elif jyzd.SYS_CLBZ == '02':
        try:
            # 登记交易流水表
            try:
                ins_lsz( int(jyzd.SYS_XTLSH), jyzd.SYS_JYRQ, jyzd.SYS_JYSJ, jyzd.SYS_JYM )
                # 对于冲正处理，直接通过02的dev做代码执行，要保存多个原流水的字段信息
                if jyzd.SYS_YLSH:
                    upd_lsz(jyzd.SYS_JYRQ,int(jyzd.SYS_XTLSH),**{'czbz':'1','yjyrq':jyzd.SYS_YJYRQ or jyzd.SYS_JYRQ,'ylsh':jyzd.SYS_YLSH})
            except PrimaryKeyError:
                logger.ods( "dev：登记交易流水表 主键重复【%s】，忽略"%(jyzd.SYS_XTLSH) ,lv = 'info',cat = 'app.tp')

            if jyzd.SYS_ZLCDEV == 'yes':
                # 在子流程内进行的测试
                # 在子流程中单独调试节点、子流程时，一定要提供SYS_YWDM
                try:
                    YW = Business(jyzd.SYS_YWDM ,memclient)
                    logger.ods( "dev：通过SYS_YWDM获取信息 成功" ,lv = 'dev',cat = 'app.tp')
                except:
                    tlog.log_exception("失败：")
                    raise RuntimeError("dev：通过SYS_YWDM获取信息 失败")

                # jyzd中加载 交易参数
                tlog.log_info("dev：交易处理--jyzd中加载 交易参数")
                jyzd.update(YW.get_ywcs())
                gghslst = YW.get_runsobj()
                logger.ods( "dev：交易处理--jyzd中加载 交易参数" ,lv = 'dev',cat = 'app.tp')

                try:
                    JY = ChildNodesFlow_CachedObject(jyzd.SYS_JYM ,memclient)
                    logger.ods( "dev：通过SYS_JYM获取信息 成功" ,lv = 'dev',cat = 'app.tp')
                except:
                    tlog.log_exception("失败：")
                    raise RuntimeError("dev：通过SYS_JYM获取信息 失败")
            else:
                # 在交易内进行的测试，SYS_SFZLC为新增的参数
                # 交易对象
                try:
                    JY = Transaction(jyzd.SYS_JYM ,memclient)
                    logger.ods( "dev：通过SYS_JYM获取信息 成功" ,lv = 'dev',cat = 'app.tp')
                except:
                    tlog.log_exception("失败：")
                    raise RuntimeError("dev：通过SYS_JYM获取信息 失败")
                # jyzd中加载 交易参数
                tlog.log_info("dev：交易处理--jyzd中加载 交易参数")
                jyzd.update(JY.get_jycs_all())
                gghslst = JY.get_jygghs()
                logger.ods( "dev：交易处理--jyzd中加载 交易参数" ,lv = 'dev',cat = 'app.tp')

            # 初始化执行环境
            tlog.log_info("dev：交易处理--初始化执行环境")
            try:
                jycl = FlowDynamicRuntime(gghslst,JY, jyzd)
                logger.ods( "dev：交易流程初始化 成功" ,lv = 'dev',cat = 'app.tp')
            except:
                tlog.log_exception("失败：")
                raise RuntimeError("dev：交易流程初始化 失败")
            jycl.np['tlog'] = tlog

            # 系统的级别
            t_xtl = get_xtcs("SYS_XTCLLEVEL" ,"0")
            # 交易的级别
            t_jyl = jyzd.SYS_JYLEVEL or "-1"
            # 当 SYS_JYLEVEL 大于0，且小于SYS_XTCLLEVEL时，交易失败
            if int(t_jyl) >0 and int(t_xtl) > int(t_jyl):
                raise RQCLError("dev：系统级别[%s],交易级别[%s],交易暂停处理"%(t_xtl, t_jyl))

            tlog.log_info("dev：交易处理--交易节点代码执行")
            # 需要根据类型不同进行不同的类初始化
            if jyzd.SYS_JYLX == '02':
                # 这是交易中的子流程测试，jyjdgz中要展示子流程的编码，通过前台获得
                try:
                    callobj = ChildNodesFlow_CachedObject(jyzd.SYS_DZXJDDM,jyzd.SYS_ZLCBM ,memclient)
                    logger.ods( "dev：通过SYS_DZXJDDM获取信息 成功" ,lv = 'dev',cat = 'app.tp')
                except:
                    tlog.log_exception("失败：")
                    raise RuntimeError("dev：通过SYS_DZXJDDM获取信息 失败")
            else:
                # 仅能进行py节点的测试，不能测试pyc、c等，这类需要jylc中的cs信息，获取不到
                try:
                    callobj = TransactionNode(jyzd.SYS_DZXJDDM ,memclient)
                    logger.ods( "dev：通过SYS_DZXJDDM获取信息 成功" ,lv = 'dev',cat = 'app.tp')
                except:
                    tlog.log_exception("失败：")
                    raise RuntimeError("dev：通过SYS_DZXJDDM获取信息 失败")
            # call的结果
            jyzd.SYS_JYJDZXJG = jycl.call(callobj)
            jyzd.SYS_CLBZ = '03'
            tlog.log_info("dev：交易处理--处理结束" ,jyzd=jyzd )
            logger.ods( "dev：交易处理--处理结束 成功" ,lv = 'dev',cat = 'app.tp')
        except RQCLError:
            logger.oes( 'dev：系统日切，交易处理失败：' ,lv = 'warning',cat = 'app.tp')
            tlog.log_exception("dev：交易处理失败：")
            # 为jyzd.SYS_RspCode赋值“TS9999”、jyzd.SYS_RspInfo赋值“交易执行异常”
            err_rqcl(jyzd)
        except:
            logger.oes( 'dev：交易处理--处理失败：'+str(jyzd) ,lv = 'error',cat = 'app.tp')
            tlog.log_exception("dev：交易处理--处理失败：")
            # 为jyzd.SYS_RspCode赋值“TS9999”、jyzd.SYS_RspInfo赋值“交易执行异常”
            err_comm(jyzd)
    if memclient:
        memclient.disconnect_all()
        logger.ods( "dev：memclient关闭 成功" ,lv = 'dev',cat = 'app.tp')
    return jyzd


def main(jyzd):
    """
        1.初始化jyzd：交易日期时间
        2.判断SYS_ISDEV：
           若为None值调用jycl函数，进行处理；
           若非None值，初始化jyzd中系统流水号、交易日期、响应码、响应内容，再调用jycl_dev进行处理，业务处理完成后根据xym值判断交易状态，然后更新交易流水表中的交易信息。
    """
    try:
        # 交易创建时间
        _jyrq = datetime.datetime.now().strftime('%Y%m%d')
        _jysj = datetime.datetime.now().strftime('%H%M%S')

        jyzd = AttrDict(jyzd)
        # 系统流水号 日期内唯一。TP在“交易识别时”即于DB获取初始化该字段。
        if not jyzd.SYS_XTLSH:
            # 正常三方发起的交易，会在01时初始化SYS_XTLSH，02的时候就已经有了
            # 自动发起交易，进来的时候是02，也需要赋值
            # 单步调试，只会进来一次，所以要做赋值
            jyzd.SYS_XTLSH = get_xtlsh()

        if not jyzd.SYS_RspCode:
            # jyzd.SYS_RspCode初始取值为“000000”；jyzd.SYS_RspInfo初始取值为“交易成功”。
            jyzd.SYS_RspCode = "000000"
            jyzd.SYS_RspInfo = "交易成功"

        if not jyzd.SYS_JYRQ:
            # 系统日期 YYYYMMDD。TP在“交易识别时”即于DB获取初始化该字段。
            jyzd.SYS_JYRQ = _jyrq
        if not jyzd.SYS_XTRQ:
            # 2015-07-16 新增
            jyzd.SYS_XTRQ = _jyrq

        # 用于冲正处理
        if not jyzd.HTXX:
            jyzd.HTXX = "{}"
        if not jyzd.SJ_XH:
            jyzd.SJ_XH = "0"
        if not jyzd.ISSAF:
            jyzd.ISSAF = "no"

        jyzd.SYS_JYSJ = _jysj
        jyzd.SYS_XTSJ = _jysj

        # 全局的日志对象
        tlog.set_data(jyzd)

        logger.ods( '当前处理的交易: SYS_XTLSH：%s  SYS_CLBZ：%s'%(str(jyzd.SYS_XTLSH),jyzd.SYS_CLBZ) ,lv = 'dev',cat = 'app.tp')

        if jyzd.SYS_ISDEV is None:
            # 生产交易日志，root/日期/通讯节点/pid/流水号
            # 流水号做文件名
            set_tlog_parms(tlog ,jyzd.SYS_TXJBID ,filename=jyzd.SYS_XTLSH)
            jycl(jyzd)
            tlog.close(jyzd.SYS_XTLSH)
        else:
            # 单步调试日志，会使用rpc方式，不会用本地文件方式
            tlog.set_rpctype()
            # 系统流水号 日期内唯一。TP在“交易识别时”即于DB获取初始化该字段。
            jycl_dev(jyzd)
            # 调整回默认配置
            tlog.set_rpctype(logtype="file")

            jyjszt = jyjszt_dict.get(jyzd.SYS_RspCode,"10")
            # SYS_JYJDGZ_HIS 是为了能够在冲正的处理时，将SYS_JYJDGZ的值做追加更新
            upd_lsz(jyzd.SYS_JYRQ,int(jyzd.SYS_XTLSH),**{'zt':jyjszt,'xym':jyzd.SYS_RspCode,'xynr':jyzd.SYS_RspInfo[:1000],'jyjssj':e_now(),'jyjdgz':(jyzd.SYS_JYJDGZ_HIS or '')+(jyzd.SYS_JYJDGZ or '')})

        # 返回给调用方的值、是否继续运行
        logger.ods( '当前处理的交易: SYS_XTLSH：%s 正常结束，返回值： SYS_CLBZ：%s '%(str(jyzd.SYS_XTLSH),jyzd.SYS_CLBZ) ,lv = 'info',cat = 'app.tp')
        return jyzd.to_dict()
    except:
        logger.oes( '交易处理出现异常'+str(jyzd) ,lv = 'error',cat = 'app.tp')
        exc_msg = traceback2.format_exc()
        return {"SYS_CLBZ":"03" ,"SYS_YFSDBW":str(exc_msg).encode('utf8') ,"SYS_CSSJ":"-1"}

def test_():
    # SYS_JSDDBW 接收到的报文
    # SYS_YFSDBW 要发送的报文
    test_bw = AttrDict({'SYS_CLBZ':'01', 'SYS_JSDDBW':b'lt001aaaaaa20150226', 'SYS_TXJBID':'ltdls_tx'})
    print('第一次处理start 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('第一次处理over 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('第二次处理over 报文字典的情况：', repr(test_bw))

def test_jycl_jd():
    print("***************** 通讯解包函数 *******************************")
    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_CLBZ':'01','SYS_JSDDBW':b'lt001aaaaaa20150226','SYS_TXJBID':'ltdls_tx'})
    print('处理前 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('处理后 报文字典的情况：', repr(test_bw))
    print("***************** 正常的节点 *******************************")
    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_JYLX':'03', 'SYS_DZXJDDM':'zzdsf_gm_ltjfycl的UUID', 'SYS_CLBZ':'02','SYS_CSSJ':60,'SYS_JSDDBW':b'lt001aaaaaa20150226','SYS_JYM':'lt001','SYS_TXJBID':'ltdls_tx'})
    print('处理前 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('处理后 报文字典的情况：', repr(test_bw))
    print("***************** 解包节点 *******************************")
    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_JYLX':'03', 'SYS_DZXJDDM':'unpack_beai_540003_32位UUID', 'SYS_CLBZ':'02','SYS_CSSJ':60,'SYS_JSDDBW':b'lt001aaaaaa20150226','SYS_JYM':'lt001','SYS_TXJBID':'ltdls_tx'})
    print('处理前 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('处理后 报文字典的情况：', repr(test_bw))
    print("***************** 打包节点 *******************************")
    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_JYLX':'03', 'SYS_DZXJDDM':'pack_beai_540003_32位UUID', 'SYS_CLBZ':'02','SYS_CSSJ':60,'SYS_JSDDBW':b'lt001aaaaaa20150226','SYS_JYM':'lt001','SYS_TXJBID':'ltdls_tx'})
    print('处理前 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('处理后 报文字典的情况：', repr(test_bw))
    print("***************** 交易中测试子流程 *******************************")
    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_JYLX':'02', 'SYS_DZXJDDM':'ltjf_zlc的UUID','SYS_ZLCBM':"ltjf_zlc", 'SYS_CLBZ':'02','SYS_CSSJ':60,'SYS_JSDDBW':b'lt001aaaaaa20150226','SYS_JYM':'lt001','SYS_TXJBID':'ltdls_tx'})
    print('处理前 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('处理后 报文字典的情况：', repr(test_bw))
    print("***************** 子流程中的节点 提供交易码测试 *******************************")
    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_JYLX':'03', 'SYS_DZXJDDM':'dsyw_pack_beai_510001的节点ID', 'SYS_CLBZ':'02','SYS_CSSJ':60,'SYS_JSDDBW':b'lt001aaaaaa20150226','SYS_JYM':'lt001','SYS_TXJBID':'ltdls_tx'})
    print('处理前 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('处理后 报文字典的情况：', repr(test_bw))
    print("***************** 子流程中测试节点 *******************************")
    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_JYLX':'03', 'SYS_DZXJDDM':'dsyw_pack_beai_510001的节点ID', 'SYS_CLBZ':'02','SYS_CSSJ':60 ,'SYS_ZLCDEV':'yes', 'SYS_YWDM':'ltdls', 'SYS_JYM':'ltjf_zlc的UUID'})
    print('处理前 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('处理后 报文字典的情况：', repr(test_bw))
#    print("***************** 子流程中测试子流程 *******************************")
#    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_JYLX':'02', 'SYS_DZXJDDM':'ltjf_zlc的UUID_2', 'SYS_CLBZ':'02','SYS_CSSJ':60 ,'SYS_ZLCDEV':'yes', 'SYS_YWDM':'ltdls', 'SYS_JYM':'ltjf_zlc的UUID'})
#    print('处理前 报文字典的情况：', repr(test_bw))
#    test_bw = main(test_bw)
#    print('处理后 报文字典的情况：', repr(test_bw))
    print("***************** 子流程中测试子流程 *******************************")
    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_JYLX':'02', 'SYS_DZXJDDM':'ltjf_zlc的UUID_2', 'SYS_CLBZ':'02','SYS_CSSJ':60 ,'SYS_ZLCDEV':'yes', 'SYS_YWDM':'ltdls', 'SYS_JYM':'ltjf_zlc的UUID'})
    print('处理前 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('处理后 报文字典的情况：', repr(test_bw))


def test____():
    suc_buf = "397 ZZ02            (dp1\nS'SJGM_SPECIALS'\np2\nS'SYS_RspCode,XYM|SYS_RspInfo,XYNR,CXXYXX'\np3\nsS'HMLX'\np4\nS'G'\nsS'JYJGM'\np5\nS'5500'\np6\nsS'CZGY'\np7\nS'admin'\np8\nsS'JFHM'\np9\nS'13583128471'\np10\nsS'DQDM'\np11\ng6\nsS'SJGM_FIELDS'\np12\nS'XYM,XYNR,CXXYXX,YHMC,HFYE'\np13\nsS'QDLSH'\np14\nS'11111Z000003'\np15\nsS'QDBH'\np16\nS'00'\np17\nsS'JYDM'\np18\nS'ZZ02'\np19\nsS'QDJYRQ'\np20\nS'20150312'\np21\nsS'ZDID'\np22\nS'11111'\np23\ns."
    fil_buf = "397 ZZ02            (dp1\nS'SJGM_SPECIALS'\np2\nS'SYS_RspCode,XYM|SYS_RspInfo,XYNR,CXXYXX'\np3\nsS'HMLX'\np4\nS'H'\nsS'JYJGM'\np5\nS'5500'\np6\nsS'CZGY'\np7\nS'admin'\np8\nsS'JFHM'\np9\nS'13583128471'\np10\nsS'DQDM'\np11\ng6\nsS'SJGM_FIELDS'\np12\nS'XYM,XYNR,CXXYXX,YHMC,HFYE'\np13\nsS'QDLSH'\np14\nS'11111Z000003'\np15\nsS'QDBH'\np16\nS'00'\np17\nsS'JYDM'\np18\nS'ZZ02'\np19\nsS'QDJYRQ'\np20\nS'20150312'\np21\nsS'ZDID'\np22\nS'11111'\np23\ns."
    test_bw = AttrDict({'SYS_CLBZ':'01', 'SYS_JSDDBW':suc_buf, 'SYS_TXJBID':'gm_tx'})
    print('第一次处理start 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('第一次处理over 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('第二次处理over 报文字典的情况：', repr(test_bw))


def test_dev():
    # SYS_JSDDBW 接收到的报文
    # SYS_YFSDBW 要发送的报文
    test_bw = AttrDict({'SYS_ISDEV':'yes', 'SYS_CLBZ':'01','SYS_JSDDBW':b'lt001aaaaaa20150226','SYS_TXJBID':'ltdls_tx'})
    print('第一次处理start 报文字典的情况：', repr(test_bw))
    test_bw = main(test_bw)
    print('第一次处理over 报文字典的情况：', repr(test_bw))


if __name__=="__main__":
    test_jycl_jd()
