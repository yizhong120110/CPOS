# -*- coding: utf-8 -*-
"""
    LP 
      日志处理进程启动脚本
      LP继承了RpclogApp，重写了父类中的on_start和stop函数
      父类RpclogApp中实现了进程信息的汇报，子类LP中增加业务处理的逻辑部分
      启动方式为 python34 app.py -p 10012 -T filelpapp -i 1000_1 -t 3 -w 10 rpclog
"""
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.application.app_rpclog import env_get ,env_set ,env_clone
from cpos.esb.basic.application.app_ctrle_rpclog import RpclogEApp
import cpos.esb.basic.rpc.rpc_log as rlog
import cpos.esb.app.lp.log_file as filelp
import cpos.esb.app.lp.log_rpc as rpclp


def service (received):
    """
       调用basic层rpc_log中提供的函数，在接收到LP对应的消息队列发过来的消息后阻塞执行线程service回调函数
       service函数中有返回值（return None , False），第二个参数为False执行stop函数
    """
    logger.ods( '-------------------------------------------',lv = 'dev',cat = 'app.rpclp')
    # 这是单步调试中使用的，放开问题不大
    logger.ods( 'LP received : \n' + str(received.getcontent() ) ,lv = 'dev',cat = 'app.rpclp')
    return rpclp.content2logdb(received.getcontent()), env_get('keep_running',True)


def working_callback(msgload):
    write_type = (env_get('ProcessArgs') or [''])[-1]
    if write_type == "rpclog":
        rlog.start_log_server(service)
    else:
        """
           这里要求文件处理是一个长期型的，避免短期结束
           由于这是一个独立的线程，所以需要做sleep操作
        """
        filelp.main_all()
    return True


# 启动之初就激活E的工作线程
RpclogEApp(working_callback=working_callback,appname="LP",startwork=True).run()
