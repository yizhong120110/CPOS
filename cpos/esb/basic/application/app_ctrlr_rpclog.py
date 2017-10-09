# -*- coding: utf-8 -*-
from cpos.foundation.application.controller import ControllerApp
from cpos.esb.basic.application.app_rpclog import RpclogApp
from cpos.esb.basic.application.app_rpclog import env_set ,env_get
from cpos.esb.basic.config import settings
from cpos.esb.basic.resource.logger import *
import os


class RpclogRApp(ControllerApp,RpclogApp):
    """
        为Controller增加RPC的log信息汇报
    """
    def __init__(self,app_port ,controllee_start=None ,controllee_stop=None ,\
                    controllee_change_callback=None ,controller_idle_callback=None ,appname="RpclogRApp"):
        ControllerApp.__init__(self,app_port ,controllee_start=controllee_start ,controllee_stop=controllee_stop ,\
                    controllee_change_callback=controllee_change_callback ,controller_idle_callback=controller_idle_callback\
                    ,controllee_max=False)
        env_set('ProcessName',appname)
        # 设置logger的根目录
        logger_set_root(logger,os.path.join(settings.APPLOGPATH, env_get('ProcessName')))
        logger.ods ("新进程启动：%s"%(env_get('ProcessName')) ,lv='info',cat = 'basic.RpclogRApp')

    def on_start (self):
        ControllerApp.on_start(self)
        RpclogApp.on_start(self)

    def stopping(self):
        """
            准备停止的时候就不再做信息汇报了
        """
        ControllerApp.stopping(self)
        RpclogApp.stopping(self)
