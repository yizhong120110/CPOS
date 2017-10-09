# -*- coding: utf-8 -*-
"""
    为ICP做一次转发，将报文通过RMQ发送到TP进行处理
    TP处理超时时，统一返回以'Timeout@'开头的字符串
    启动方式为 python34 app.py -p 10031 -T icmapp -i 1000_1 -t 3 -w 10
    TP的01步骤单独处理时，需要使用下面的启动方式做代替
        # -P split 是需要与TP进程启动时的配置参数一致，配置在通讯进程类型中
    python34 app.py -p 10031 -T icmapp -i 1000_1 -t 3 -w 10 -P split
    修改ICM的启动IP时，可以使用 -I 145.1.200.71 参数
    修改ICM的启动端口时，可以使用 -s 6620 参数
    修改ICM启动时的回调函数，可以使用-c service_jym 参数
"""
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.application.app_ctrle_rpclog import RpclogEApp, env_get
import cpos.esb.basic.icm.icm_network as icm_network
import cpos.esb.basic.icm.icm_spec as icm_spec
import cpos.esb.app.icm.icm as icm
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.resource.functools import kill_process
import os, time


def service (in_frame,sync = True):
    # 进程类型，是否需要将TP的01步骤单独转发
    p_options = (env_get('ProcessOptions') or {})
    p_type = p_options.get("protocol", "")
    commnode_id,message_body = icm_spec.icm_decode_frame_payload(in_frame.payload)
    if isinstance(message_body ,bytearray):
        message_body = bytes(message_body)
    service_dict = {'SYS_CLBZ':'01', 'SYS_JSDDBW':message_body, 'SYS_TXJBID': commnode_id}
    logger.obs ("收到新的处理请求：SYS_TXJBID：%s  SYS_JSDDBW："%(commnode_id) ,block=message_body ,lv='info',cat = 'app.icm')
    rs_buf = icm.do_tp_proc('01',service_dict ,sync ,logger, p_type)
    logger.obs ("处理结果为：%s"%(rs_buf) ,lv='dev',cat = 'app.icm')
    return icm_spec.build_icm_frame( commnode_id, rs_buf )


def service_jym (in_frame,sync = True):
    commnode_id,message_body = icm_spec.icm_decode_frame_payload(in_frame.payload)
    if isinstance(message_body ,bytearray):
        message_body = bytes(message_body)
    service_dict = {'SYS_CLBZ':'02', 'SYS_JSDDBW':message_body, 'SYS_JYM': commnode_id}
    # 交易创建时间，用于登记lsz以及判断交易超时
    service_dict['SYS_CTIME'] = "%.05f"%time.time()
    service_dict['SYS_CSSJ'] = "30"
    service_dict['SYS_TXJBID'] = "SJFESB_JYM_ICM"
    logger.obs ("收到新的处理请求：SYS_JYM：%s  SYS_JSDDBW："%(commnode_id) ,block=message_body ,lv='info',cat = 'app.icm_jym')
    rs_buf = icm.do_tp_proc('02',service_dict ,sync ,logger)
    logger.obs ("处理结果为：%s"%(rs_buf) ,lv='dev',cat = 'app.icm')
    return icm_spec.build_icm_frame( commnode_id, rs_buf )


def working_callback(msgload):
    """
        进程中工作线程的回调函数
    """
    try:
#        # 有logger调用存在时，icm的停止会出异常，直接将日志通过print方式输出
#        logger.root = None
        p_options = (env_get('ProcessOptions') or {})
        ttopts = dict(cb=service)
        if p_options.get("ser_port"):
            # 数据库中TXWJMC的值应该写 xmdfy,-s 6620
            ttopts["icmport"] = p_options.get("ser_port")
        if p_options.get("ser_ip"):
            # 数据库中TXWJMC的值应该写 xmdfy,-I 145.1.200.71
            ttopts["icmip"] = p_options.get("ser_ip").strip()
        if p_options.get("callback") and p_options.get("callback").strip()=="service_jym":
            # 数据库中TXWJMC的值应该写 xmdfy,-s 6620,-c service_jym
            ttopts["cb"] = service_jym
        icm_network.start_tcp_icm_server(**ttopts)
    except:
        logger.oes ("icm 运行异常，强制停止进程，准备重启：" ,lv='error',cat = 'app.icm')
        kill_process(os.getpid())
    return True


if __name__ == '__main__':
    # 使用Pool(2)时，需要用__name__==__main__方式启动
    # 启动之初就激活E的工作线程
    RpclogEApp(working_callback=working_callback,appname="ICM",startwork=True).run()
