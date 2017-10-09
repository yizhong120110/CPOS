# -*- coding: utf-8 -*-
# OCM独立进程启动使用
from cpos.esb.basic.application.app_ctrle_rpclog import RpclogEAppAlive
from cpos.esb.basic.application.app_ctrle_rpclog import get_shell_args
from cpos.esb.basic.resource.functools import kill_process
import os


class RpclogEApp(RpclogEAppAlive):
    def stopping(self):
        """
            停止命令，防止注册的线程不能够退出
        """
        RpclogEAppAlive.stopping(self)
        kill_process(os.getpid())

