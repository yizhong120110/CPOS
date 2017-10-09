# -*- coding: utf-8 -*-
"""
    启动方式 python34 app.py -p 10010 -T jrsapp -i 1001_1 -t 5
"""
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.application.app_rpclog import env_set,env_get
from cpos.esb.basic.application.app_ctrlreh_rpclog import RpclogREHApp
from cpos.esb.basic.application.app_ctrle_startpy import controlleeapp_start
from cpos.esb.basic.resource.logger import *
import cpos.esb.basic.rpc.rpc_jr as rjr
import cpos.esb.app.jrs.jrs as jrs
import os
from cpos.esb.basic.config import settings 
ctrl_re_jr = settings.CTRL_RE_JR


def rpcmsg_to_e(received):
    logger.ods( '-------------------------------------------' ,lv = 'dev',cat = 'app.jrs')
    logger.ods( 'service received : \n' + str(received.getcontent()) ,lv = 'info',cat = 'app.jrs')
    logger.ods('-------------------------------------------' ,lv = 'dev',cat = 'app.jrs')
    # 收到的内容
    return jrs.send_msg_to_env(received.getcontent()), env_get('keep_running',True)


def working_callback(msgload):
    """
       调用basic层rpc_log中提供的函数，在接收到LP对应的消息队列发过来的消息后阻塞执行线程service回调函数
       service函数中有返回值（return None , False），第二个参数为False执行stop函数
    """
    rjr.start_jr_server(["jr"] ,rpcmsg_to_e)
    return True


def controllee_start(clientid,app_port,interval,client_type,params):
    """
        启动新的子进程
    """
    logger.ods('需要启动jr进程%s'%client_type ,lv = 'info',cat = 'app.jrs')
    jr_path = os.path.abspath( os.path.join(os.path.split(__file__)[0], '..', 'jr', 'app.py') )
    controlleeapp_start(client_type,clientid,app_port,interval,jr_path)


server = RpclogREHApp(ctrl_re_jr['port'] ,controllee_working_callback=working_callback \
                        ,controllee_start=controllee_start, controller_idle_callback=jrs.env_msg_to_r \
                        ,appname="JRS",startwork=True)

# 这里是初始化jr
server.ctk.register_configs(ctrl_re_jr['init_config'])
server.run()

