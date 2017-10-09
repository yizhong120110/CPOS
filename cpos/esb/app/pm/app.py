# -*- coding: utf-8 -*-
"""  
    进程维护，只是负责启动进程，不负责分发任务，启动后接收野孩子
    首次启动后，先不将所有进程都启动起来，待4个汇报间隔后再增加任务，目的是为了能够接管野孩子
    启动方式 python34 app.py -p 10010 -T pmapp -i 1001_1 -t 5
"""
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.application.app_ctrlreh_rpclog import RpclogREHApp
from cpos.esb.basic.application.app_rpclog import env_set,env_get,env_pop
from cpos.esb.basic.application.app_ctrle_startpy import controlleeapp_start
from cpos.esb.basic.application.app_interval import interval
import cpos.esb.basic.rpc.rpc_jr as rjr
from cpos.esb.app.pm.db_pm import get_jcpzxx ,get_interval
from cpos.esb.basic.config import settings
import copy
ctrl_re_pm = settings.CTRL_RE_PM


def controller_idle_callback(ctk):
    """
        这里应该根据数据库的值变化做进程的增减操作
        1.查询进程配置表中的数据，get_jcpzxx
        2.获取ctk中管理进程的信息
        3.1 2 的结果进程比对,生存增减操作
        jcpzxx_dic 的结构如下
        {'appfilepath': 'E:\\projects\\ZHTSYWPT\\cpos.esb.kf\\cpos\\esb\\app\\js\\app.py', 'count': 1, 'interval': 10}
        ctk.get_controllees_config() 的结构如下
        {'js': {'count': 1, 'message_list': [], 'init_config': {'appfilepath': 'E:\\projects\\ZHTSYWPT\\cpos.esb.kf\\cpos\\esb\\app\\js\\app.py', 'count': 1, 'interval': 10}, 'interval': 10}}
        
    """
    # 是否可以查询一次数据库
    jcpzxx_dic = env_pop('_pm_jcpzxx','')
    # 通过RMQ更新进程列表
    jcpzxx_rpc = env_pop('_pm_jcpzxx_rpc','')
    if jcpzxx_rpc != '':
        # 没有查询数据库，则以自己维护的列表为准
        if jcpzxx_dic == '':
            jcpzxx_dic = {}
            for kk ,vdic in ctk.get_controllees_config().items():
                jcpzxx_dic[kk] = vdic["init_config"]
        
        # jclx_parm有值就更新数据字典，没有值就尝试移除
        for jclx ,jclx_parm in jcpzxx_rpc.items():
            if jclx_parm:
                jcpzxx_dic[jclx] = jclx_parm
            elif jcpzxx_dic.get(jclx):
                jcpzxx_dic.pop(jclx)
    
    if jcpzxx_dic != '':
        # 从数据库中获得的进程信息列表，或者是从rmq中获得的任务信息，都要做进程状态更新，一起处理即可
        ctk.upload_jcpzxx(jcpzxx_dic)
    return None,True


def working_callback(msgload):
    """
       这里控制是否可以做db查询，5秒一次
    """
    try:
        env_set('_pm_jcpzxx',get_jcpzxx())
    except:
        logger.oes("数据库查询异常：" ,lv = 'error',cat = 'app.pm')

    while interval.run(get_interval() ,env_get('keep_running',True)):
        try:
            # 获得数据库的配置信息
            env_set('_pm_jcpzxx',get_jcpzxx())
        except:
            logger.oes("数据库查询异常：" ,lv = 'error',cat = 'app.pm')
    return True


def controllee_start(clientid,app_port,interval,client_type,params):
    """
        启动新的子进程
    """
    controlleeapp_start(client_type,clientid,app_port,interval,params['appfilepath'],apparg=params.get('apparg','') )


class PM(RpclogREHApp):
    """
        一个单独的线程做rpc的监听
        E的工作线程中做数据库的定时查询
        R的空闲轮询中做进程的配置信息修改
        三个线程通过env做数据交互
    """
    def setmsg_to_env (self ,received):
        jcpzxx_rpc = received.getcontent()
        logger.ods( '-------------------------------------------' ,lv = 'dev',cat = 'app.pm')
        logger.ods( 'service received : \n' + str(jcpzxx_rpc) ,lv = 'info',cat = 'app.pm')
        logger.ods('-------------------------------------------' ,lv = 'dev',cat = 'app.pm')
        rs = {"result":"setmsg_to_env faild"}
        try:
            if jcpzxx_rpc.get("source") == "pm" and isinstance(jcpzxx_rpc.get("param") ,list):
                jcxx_dic = {}
                for jclx in jcpzxx_rpc["param"]:
                    dbjcxx = get_jcpzxx(jclx)
                    jcxx_dic[jclx] = copy.deepcopy(dbjcxx.get(jclx,{}))
                env_set('_pm_jcpzxx_rpc',jcxx_dic)
                rs = {"result":"setmsg_to_env ok"}
        except:
            logger.oes("前台发起的进程管理异常：" ,lv = 'warning',cat = 'app.pm')
        return rs, env_get('keep_running',True)

    def rpcmsglistener (self):
        """
            这里用于从RMQ上获得消息
            client的发送方式为：
                senddic = {"source":"pm", "param":['cse1','sddf3']}
                send_jr_reply(senddic,'shhx-e430c',protocol='pm')
        """
        rjr.start_jr_server(["pm"] ,self.setmsg_to_env)
        self.stopping()
        return True

    def on_start (self):
        RpclogREHApp.on_start(self)
        # 这是附加一个线程
        self.register_thread('rpcmsglistener',self.rpcmsglistener)


PM(ctrl_re_pm['port'] ,controllee_working_callback=working_callback \
                        ,controllee_start=controllee_start \
                        ,controller_idle_callback=controller_idle_callback \
                        ,appname="PM",startwork=True ,controllee_max=True).run()
