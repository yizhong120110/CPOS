# -*- coding: utf-8 -*-
from cpos.foundation.substrate.utils.signal import signal_func
from cpos.esb.basic.resource.logger import *
from cpos.esb.basic.config import settings
from cpos.esb.basic.resource.functools import traceback2
import subprocess
import sys


def controlleeapp_start(client_type,clientid,app_port,interval,appfilepath,apparg='',max_waittime=600,cmd="python34"):
    """
        启动一个python的controlleeapp子进程
    """
    signal_func()
    try:
        # args 要按照参数组的方式分，不能够合并成一个参数字符串
        if apparg and (isinstance(apparg,list) or isinstance(apparg,tuple)):
            apparg = list(apparg)
        elif apparg and isinstance(apparg,str):
            apparg = [apparg]
        else:
            apparg = []
        args_tuple = [cmd ,appfilepath] + apparg + [ '-p %s'%app_port ,'-T %s'%client_type ,'-i %s'%clientid ,'-t %s'%interval ,'-w %s'%max_waittime]
        logger.ods( "启动一个新的子进程：%s"%(" ".join(args_tuple)) ,lv = 'info',cat = 'basic.application')
        # stdout stderr 两个参数一定要有，可以保证进程启动后不会出现“OSError: [Errno 5] Input/output error”
        #subprocess.Popen(args=args_tuple, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # 将print的内容重定向到指定的文件，在进程结束时才会向这里写内容
        subprocess.Popen(args=args_tuple, stdout=open(settings.PRINTFILEPATH,'ab') , stderr=open(settings.PRINTFILEPATH,'ab'))
    except:
        logger.oes("子进程启动出现异常" ,lv = 'error',cat = 'basic.application')


def shellcall(cmdstr ,isrsmsg=False):
    """
        cmdstr 被执行的命令
        isrsmsg 是否需要返回值
    """
    signal_func()
    try:
        logger.ods("将要被执行的命令为：%s,是否需要返回值：%s"%(cmdstr,str(isrsmsg)) ,lv = 'info',cat = 'basic.application')
        rsmsg = ''
        if isrsmsg:
            # 为了能够得到返回值，所以要这样处理
            p = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # 标准错误输出
            err_lines = p.stderr.readlines() if p.stderr else [] 
            
            if sys.platform[:3] == 'win':
                codingstr = "gb18030"
            else:
                codingstr = "utf8"
            # 标准输出+标准错误输出
            rsmsg = "\n".join( [ (line.decode(codingstr)).strip() for line in p.stdout.readlines() + err_lines ] )
        else:
            # 不需要返回值的
            subprocess.Popen(cmdstr, shell=True, stdout=open(settings.PRINTFILEPATH,'ab') , stderr=open(settings.PRINTFILEPATH,'ab'))
        return True ,rsmsg
    except:
        logger.oes("命令出现异常：" ,lv = 'error',cat = 'basic.application')
        exc_msg = traceback2.format_exc()
        return False ,exc_msg


def shellcall_args(args_tuple ,isrsmsg=False):
    """
        args_tuple 被执行的命令
        isrsmsg 是否需要返回值
    """
    signal_func()
    try:
        logger.ods("将要被执行的命令为：%s,是否需要返回值：%s"%(str(args_tuple),str(isrsmsg)) ,lv = 'info',cat = 'basic.application')
        rsmsg = ''
        if isrsmsg:
            # 为了能够得到返回值，所以要这样处理
            p = subprocess.Popen(args=args_tuple, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # 标准错误输出
            err_lines = p.stderr.readlines() if p.stderr else [] 
            
            if sys.platform[:3] == 'win':
                codingstr = "gb18030"
            else:
                codingstr = "utf8"
            # 标准输出+标准错误输出
            rsmsg = "\n".join( [ (line.decode(codingstr)).strip() for line in p.stdout.readlines() + err_lines ] )
        else:
            # 不需要返回值的
            subprocess.Popen(args=args_tuple, stdout=open(settings.PRINTFILEPATH,'ab') , stderr=open(settings.PRINTFILEPATH,'ab'))
        return True ,rsmsg
    except:
        logger.oes("命令出现异常：" ,lv = 'error',cat = 'basic.application')
        exc_msg = traceback2.format_exc()
        return False ,exc_msg
