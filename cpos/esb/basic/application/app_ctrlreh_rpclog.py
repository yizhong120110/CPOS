# -*- coding: utf-8 -*-
from cpos.foundation.application.controllee import get_shell_args
from cpos.foundation.application.controllereh import ControlleREHApp
from cpos.esb.basic.application.app_rpclog import RpclogApp
from cpos.esb.basic.application.app_rpclog import env_set ,env_get
from cpos.esb.basic.config import settings
from cpos.esb.basic.resource.logger import *
import os

class RpclogREHApp(ControlleREHApp,RpclogApp):
    """
        增加RPC的log信息汇报
    """
    def __init__(self ,r_app_port ,controllee_working_callback=None, controllee_start=None ,controllee_stop=None \
                    , controllee_change_callback=None ,controller_idle_callback=None ,appname="RpclogREHApp" \
                    ,startwork=False ,controllee_max=False):

        options ,args = get_shell_args()
        ControlleREHApp.__init__ (self, options['client_type'], options['clientid'], options['app_port'], options['interval'] ,r_app_port \
                        , e_max_waittime=options['max_waittime'], e_working_callback = controllee_working_callback, e_startwork = startwork \
                        , r_controllee_start=controllee_start ,r_controllee_stop=controllee_stop \
                        , r_controllee_change_callback=controllee_change_callback ,r_idle_callback=controller_idle_callback \
                        , r_controllee_max=controllee_max )
        env_set('ProcessName',appname)
        env_set('ProcessOptions',options)
        env_set('ProcessArgs',args)
        # 设置logger的根目录
        logger_set_root(logger,os.path.join(settings.APPLOGPATH, env_get('ProcessName')))
        logger.ods ("新进程启动：%s"%(env_get('ProcessName')) ,lv='info',cat = 'basic.RpclogREHApp')

    def on_start (self):
        ControlleREHApp.on_start(self)
        RpclogApp.on_start(self)

    def stopping(self):
        """
            准备停止的时候就不再做信息汇报了
        """
        ControlleREHApp.stopping(self)
        RpclogApp.stopping(self)
