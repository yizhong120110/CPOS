# -*- coding: utf-8 -*-

"""
Descriptions
"""
from cpos.foundation.application.env import env_get ,env_set ,env_clone ,env_pop
from cpos.foundation.application.framework import Application
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.resource.functools import get_hostname
import cpos.esb.basic.rpc.rpc_log as rlog
import os
import time


class RpclogApp(Application):
    """
        向RPC中做日志汇报的线程
    """
    def thread_monitor (self):
        while env_get('monitor_keep_running',True):
            env_set('pid',os.getpid())
            env_set('hostip',get_hostname())
            env_set('hosttime',time.strftime('%Y%m%d%H%M%S') )
            #rlog.send_appstatus({'appstatus':env_clone()})
            time.sleep(5)
        return True

    def on_start (self):
        Application.on_start(self)
        self.register_thread('monitor',self.thread_monitor)

    def stopping (self):
        """
            停止是个过程性操作
        """
        env_set('monitor_keep_running',False)
        logger.ods ("%s"%('停止向RPC服务器的自动汇报线程') ,lv='info',cat = 'basic.rpclogapp')
