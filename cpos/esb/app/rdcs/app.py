# -*- coding: utf-8 -*-
""" 
    rdcs启动app：
        rdcs为REH类型进程
        rdcs进程启动后，业务处理线程执行idle_callback回掉函数中增加或删除rdc进程配置信息，
        rdcs的进程管理线程依据进程配置信息字典和进程管理规则实现rdc进程的启动和关闭；
        rdc业务处理线程加载执行的业务处理函数里用while循环的方式使任务一直处于执行状态，
        也就是一个rdc对应一个采集指标，一个rdc进程一直在执行一个任务。
        启动方式为：python34 app.py -t 4 -T 4 -i 3 -p 10231
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
from cpos.esb.basic.resource.functools import get_hostname
from cpos.esb.app.rdcs.db_rdcs import get_cjzb ,get_interval
import pickle
import binascii
import os
from cpos.esb.basic.config import settings
ctrl_rdcs = settings.CTRL_RDCS


def controller_idle_callback(ctk):
    """
        这里应该根据数据库的值变化做进程的增减操作
        1.查询进程配置表中的数据，get_cjzb
        2.获取ctk中管理进程的信息
        3.1 2 的结果进程比对,生存增减操作
    """
    # 是否可以查询一次数据库
    rdcs_info = env_pop('_rdcs_info','')
    if rdcs_info != '':
        # 获得数据库的配置信息
        jcpzxx_dic = {}
        for t_dic in rdcs_info:
            jcpzxx_dic[t_dic["wym"]] = {"apparg":str(binascii.b2a_hex(pickle.dumps(t_dic)))[2:-1].upper()}
            jcpzxx_dic[t_dic["wym"]].update(ctrl_rdcs)
        ctk.upload_jcpzxx(jcpzxx_dic)
    return None,True


def working_callback(msgload):
    """
       这里控制是否可以做db查询
    """
    zjip = get_hostname()
    try:
        env_set('_rdcs_info',get_cjzb(zjip) )
    except:
        logger.oes("数据库查询异常：" ,lv = 'error',cat = 'app.rdcs')

    while interval.run(get_interval(),env_get('keep_running',True)):
        try:
            env_set('_rdcs_info',get_cjzb(zjip) )
        except:
            logger.oes("数据库查询异常：" ,lv = 'error',cat = 'app.rdcs')
    return True


def controllee_start(clientid,app_port,interval,client_type,params):
    """
        启动新的子进程
    """
    rdc_path = os.path.abspath( os.path.join(os.path.split(__file__)[0], '..', 'rdc', 'app.py') )
    controlleeapp_start(client_type,clientid,app_port,interval,rdc_path,apparg=params.get('apparg','') ,max_waittime=params.get('max_waittime',0) )


RpclogREHApp(ctrl_rdcs['port'] ,controllee_working_callback=working_callback \
                        ,controllee_start=controllee_start \
                        ,controller_idle_callback=controller_idle_callback \
                        ,appname="RDCS",startwork=True ,controllee_max=True).run()
