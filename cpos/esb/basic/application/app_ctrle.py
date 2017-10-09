# -*- coding: utf-8 -*-
from cpos.foundation.application.controllee import ControlleeApp ,get_shell_args
from cpos.esb.basic.application.app_rpclog import env_set ,env_get
from cpos.esb.basic.config import settings
from cpos.esb.basic.resource.logger import *
from cpos.esb.basic.resource.functools import kill_process
import os


class EApp(ControlleeApp):
    """
        通过命令行方式启动app
    """
    def __init__(self ,working_callback ,appname="EApp" ,startwork=False):
        options ,args = get_shell_args()
        ControlleeApp.__init__ (self, options['client_type'], options['clientid'], options['app_port'], options['interval']\
                            , max_waittime=options['max_waittime'], working_callback = working_callback ,startwork=startwork)
        env_set('ProcessName',appname)
        env_set('ProcessOptions',options)
        env_set('ProcessArgs',args)
        # 设置logger的根目录
        logger_set_root(logger,os.path.join(settings.APPLOGPATH, env_get('ProcessName')))
        logger.ods ("新进程启动：%s"%(env_get('ProcessName')) ,lv='info',cat = 'basic.EApp')

    def stopping(self):
        """
            停止命令，防止注册的线程不能够退出
        """
        ControlleeApp.stopping(self)
        kill_process(os.getpid())

