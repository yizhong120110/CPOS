# -*- coding: utf-8 -*-
from cpos.foundation.application.controllee import ControlleeApp ,get_shell_args
from cpos.esb.basic.application.app_rpclog import RpclogApp
from cpos.esb.basic.application.app_rpclog import env_set ,env_get
from cpos.esb.basic.config import settings
from cpos.esb.basic.resource.logger import *
import os


class RpclogEApp(ControlleeApp,RpclogApp):
    """
        通过命令行方式启动app
    """
    def __init__(self, working_callback = None ,appname="RpclogEApp" ,startwork=False):
        options ,args = get_shell_args()
        ControlleeApp.__init__ (self, options['client_type'], options['clientid'], options['app_port'], options['interval']
                    , working_callback = working_callback, max_waittime=options['max_waittime'] ,startwork=startwork)
        env_set('ProcessName',appname)
        env_set('ProcessOptions',options)
        env_set('ProcessArgs',args)
        # 设置logger的根目录
        logger_set_root(logger,os.path.join(settings.APPLOGPATH, env_get('ProcessName')))
        logger.ods ("新进程启动：%s"%(env_get('ProcessName')) ,lv='info',cat = 'basic.RpclogEApp')

    def on_start (self):
        ControlleeApp.on_start(self)
        RpclogApp.on_start(self)

    def stopping(self):
        RpclogApp.stopping(self)
        ControlleeApp.stopping(self)


class RpclogEAppAlive(RpclogEApp):
    """
        一直存活的RpclogEApp，不会延迟停止
    """
    def reporting_thread(self):
        """
            E部分的汇报线程，这里会有延迟停止的处理
            通过register_thread方式添加线程，不能自动停止，所以重写此方法
        """
        env_set('keep_waiting', 'no')
        return RpclogEApp.reporting_thread(self)
