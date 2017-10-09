# -*- coding: utf-8 -*-
""" 
    JS 
      定时任务发起进程启动脚本
      JS继承了RpclogApp，重写了父类中的on_start和stop函数
      父类RpclogApp中实现了进程信息的汇报，子类JS中增加业务处理的逻辑部分
      启动方式为：python34 app.py -t 4 -T js -i 3 -p 5614
"""
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.rpc.rpc_jr import send_jr_noreply
from cpos.esb.basic.application.app_rpclog import env_get
from cpos.esb.basic.application.app_ctrle_rpclog import RpclogEApp
from cpos.esb.basic.application.app_interval import interval
from cpos.esb.basic.resource.logger import logger
from cpos.esb.app.js.db_js import get_rw ,get_interval


def main():
    # 定时任务处理进程要执行的主函数
    try:
        logger.ods( '定时任务发起进程启动' ,lv = 'dev',cat = 'app.js')
        # 1.获取今天当前时间点之前，还未发起的任务,并将任务状态更新为 9 正在执行中
        rw_lst = get_rw()
        if rw_lst:
            logger.ods( '获取到的任务个数：%s'%len(rw_lst) ,lv = 'info',cat = 'app.js')
        # 2.根据任务同步异步标志调用相应的消息存放函数
        for rwline in rw_lst:
            logger.ods( '任务id：%s'%rwline[1] ,lv = 'dev',cat = 'app.js')
            # 参数1：{任务id、任务类别}，参数2：主机名
            send_jr_noreply({'rwid':rwline[1],'source':rwline[0]},rwline[2])
        if rw_lst:
            logger.ods( '任务调用完毕',lv = 'info',cat = 'app.js')
    except:
        logger.oes( '检索定时任务过程中异常',lv = 'error',cat = 'app.js')


def working_callback(msgload):
    """
        进程中工作线程的回调函数
    """
    main()
    while interval.run(get_interval(),env_get('keep_running',True)):
        main()
    return True


# 启动之初就激活E的工作线程
RpclogEApp(working_callback=working_callback,appname="JS",startwork=True).run()
