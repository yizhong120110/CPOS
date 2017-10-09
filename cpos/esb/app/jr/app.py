# -*- coding: utf-8 -*-
""" 
    响应动作
    启动方式 python34 app.py -p 5613 -T qt -i 1001_1 -t 5
    作为独立进程存在，直接使用from import 方式加载固定的函数即可
"""
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.application.app_rpclog import env_get
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.application.app_ctrle import EApp
import json


def working_callback (msgload):
    """
        统一模式，多个type的处理
    """
    logger.ods( '-------------------------------------------',lv = 'dev',cat = 'app.jr')
    logger.ods( 'jr received : \n' + str(msgload) ,lv = 'info',cat = 'app.jr')
    # 进程的类型就是要引用模块名
    ProcessOptions = env_get('ProcessOptions')
    client_type = ProcessOptions["client_type"]
    try:
        # main函数要在exec中执行，在外面执行的时候报错了
        exec("from jr_%s import main"%(client_type))
        exec("main(json.loads(msgload))")
    except:
        logger.oes( "【%s】模块加载失败："%(client_type) ,lv = 'error',cat = 'app.jr')
    return True


EApp(working_callback=working_callback,appname="JR").run()
