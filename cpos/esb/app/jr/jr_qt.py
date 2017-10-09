# -*- coding: utf-8 -*-
"""
    前台直接发起：先是数据库备份
"""
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.application.app_ctrle_startpy import shellcall


def main(received_data):
    try:
        cslst = received_data.get('param','')        
        # 1.前台直接发起的响应动作
        czzl = cslst[0]
        rs = shellcall( czzl ,isrsmsg=True )
        logger.ods( '前台直接发起的响应动作 命令执行完成',lv = 'info',cat = 'app.jr_qt')
        return rs  
    except:
        logger.oes( '任务执行过程中异常',lv = 'error',cat = 'app.jr_qt')
        return '任务执行过程中异常'
