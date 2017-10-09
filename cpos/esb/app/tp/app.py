# -*- coding: utf-8 -*-
"""
    启动方式为 python34 app.py -p 10021 -T tpapp -i 1000_1 -t 3 -w 10
    tp的01步骤单独处理时，需要启动第二个进程：
        -P split 配置在通讯进程类型中
        # split 将tp的交易码解析拆分开
        # long 处理时间特别长的tp02部分
        # 可以增加其他的参数类型，只需jyzd中SYS_TRANS_TIME_TYPE的值与其对应
    python34 app.py -p 10021 -T tpapp01 -i 1000_1 -t 3 -w 10 -P split
"""
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.application.app_rpclog import env_get ,env_set ,env_clone
from cpos.esb.basic.application.app_ctrle_rpclog import RpclogEAppAlive
from cpos.esb.basic.application.app_interval import interval
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.resource.functools import get_uuid ,kill_process
import cpos.esb.basic.rpc.rpc_transaction as rtrans
import cpos.esb.app.tp.transaction as trans
import queue
import os

class TP(RpclogEAppAlive):
    def __init__(self ,appname):
        RpclogEAppAlive.__init__(self,appname=appname)
        # 这个是为了知道任务开始了，然后在结束的时候做一次时间处理
        self.tp_Q = queue.Queue()

    def working_service(self ,received):
        logger.ods ("-------------------------------------------" ,lv='dev',cat = 'app.tp')
        jyzd = received.getcontent()
        # 用于TP超时的情况下登记冲正流水、更新交易状态
        tp_uuid = get_uuid()
        logger.ods ("接收到的消息：%s ,%s" %(tp_uuid ,str(jyzd)) ,lv='info',cat = 'app.tp')
        # 任务处理开始了    参数1是标志，参数2是超时时间
        self.tp_Q.put( (tp_uuid ,float(jyzd.get('SYS_CSSJ') or 60) ) )
        rs = trans.main(jyzd)
        # 任务处理结束了    参数1是标志，参数2是超时时间
        self.tp_Q.put( (tp_uuid ,float(jyzd.get('SYS_CSSJ') or 60) ) )
        return rs, env_get('keep_running',True)

    def working_rpcstart(self):
        """
            进程中工作线程的回调函数
        """
        p_options = (env_get('ProcessOptions') or {})
        p_type = p_options.get("protocol", "")
        rtrans.start_trans_with_protocol([p_type.lower()], self.working_service)
        return True

    def working_timeout(self):
        """
            控制任务执行时间，避免死循环的出现
            1秒检查一次
        """
        cnt = 60
        last_uuid = None
        while interval.run(1 ,env_get('keep_running',True)):
            # 如果是空的，有两种情况，1-没有任务，2-任务没有处理完成
            # 不是空，1-上一个任务处理完成，后面可能有新任务，也可能没有；2-新任务，之前没有过任务
            while not self.tp_Q.empty():
                # 获得任务
                t_uuid ,cssj = self.tp_Q.get()
                if t_uuid == last_uuid:
                    # 这个是结束
                    last_uuid = None
                else:
                    # 这个是开始
                    last_uuid = t_uuid
                    # 避免后面开始计数时，第一次多减1
                    cnt = cssj + 1
            if last_uuid:
                # 上面的循环能够保证进入到这里的是最后任务开始了
                cnt -= 1
                logger.ods ("当前处理任务剩余时间为：%s ,%s" %(last_uuid ,cnt) ,lv='dev',cat = 'app.tp')
                if -1 > cnt:
                    logger.ods ("任务处理超时，进程自杀：%s ,%s" %(last_uuid ,os.getpid()) ,lv='info',cat = 'app.tp')
                    trans.tlog.log_info("任务处理超时，TP进程自杀，进程号：%s" %(os.getpid()))
                    try:
                        if trans.tlog.d.SYS_XTLSH:
                            # 交易超时的情况下，更新一下交易状态为TS9999
                            trans.err_comm(trans.AttrDict({"SYS_JYRQ":trans.tlog.d.SYS_JYRQ,"SYS_XTLSH":trans.tlog.d.SYS_XTLSH}))
                            # 需要判断是否是存在htrz内容
                            if trans.cnt_hyrz(trans.tlog.d.SYS_JYRQ, trans.tlog.d.SYS_XTLSH):
                                trans.ins_jycz( trans.tlog.d.SYS_XTLSH, trans.tlog.d.SYS_JYRQ, cs = 0 )
                    except:
                        trans.tlog.log_exception("任务处理超时，登记冲正信息失败：")
                    trans.tlog.close(trans.tlog.filename)
                    kill_process( os.getpid() )
        return True

    def on_start (self):
        RpclogEAppAlive.on_start(self)
        # 这是附加一个线程
        self.register_thread('working_rpcstart',self.working_rpcstart)
        self.register_thread('working_timeout',self.working_timeout)


TP(appname="TP").run()
