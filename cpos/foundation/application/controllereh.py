# -*- coding: utf-8 -*-
"""
    进程管理client-server端
    首先是client端，同时也是另一批client的server
"""
from .controller import ControllerApp
from .controllee import ControlleeApp
from .env import env_set


class ControlleREHApp(ControllerApp, ControlleeApp):

    """
        R和E本身都是线程方式的，所以使用拼接就可以做到合并
    """

    def __init__(self, e_client_type, e_clientid, e_server_port, e_interval_time, r_app_port, e_max_waittime=600, e_working_callback=None, e_startwork=False, r_controllee_start=None, r_controllee_stop=None, r_controllee_change_callback=None, r_idle_callback=None, r_controllee_max=False):
        ControlleeApp.__init__(self, e_client_type, e_clientid, e_server_port, e_interval_time, max_waittime=e_max_waittime, working_callback=e_working_callback, startwork=e_startwork)
        ControllerApp.__init__(self, r_app_port, controllee_start=r_controllee_start, controllee_stop=r_controllee_stop,
                               controllee_change_callback=r_controllee_change_callback, controller_idle_callback=r_idle_callback,
                               controllee_max=r_controllee_max)

    def on_start(self):
        ControlleeApp.on_start(self)
        ControllerApp.on_start(self)

    def stopping(self):
        """
            不管是R的部分决定了自己要停止，还是E的部分决定了自己要停止，都应该将停止影响到另外的部分
        """
        ControlleeApp.stopping(self)
        ControllerApp.stopping(self)

    def reporting_thread(self):
        """
            E部分的汇报线程，这里会有延迟停止的处理
            作为REH存在时，应该保证其长驻，不能自动停止，所以重写此方法
        """
        env_set('keep_waiting', 'no')
        return ControlleeApp.reporting_thread(self)
