# -*- coding: utf-8 -*-
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.application.app_rpclog import env_set,env_get
from cpos.esb.basic.application.app_ctrlr_rpclog import RpclogRApp
from cpos.esb.basic.resource.logger import *
import time
from cpos.esb.basic.config import settings 
ctrl_reh_jrs = settings.CTRL_REH_JRS


class JRSStop(RpclogRApp):
    """
        用于停止jrs
        由于R没有单独的任务处理线程，所以需要附加一个线程
    """
    def jobResponder (self):
        time.sleep(ctrl_reh_jrs['interval']*4)
        logger.ods ("%s"%('进程任务处理结束') ,lv='info',cat = 'app.jrs_stop_app')
        self.stopping()
        return True

    def on_start (self):
        RpclogRApp.on_start(self)
        self.register_thread('jobResponder',self.jobResponder)

JRSStop(app_port=ctrl_reh_jrs['port'], appname="JRSStop").run()
