#!/usr/bin/env python3
# -*- coding: utf-8 -*-
try:
    from . import loader
except:
    import loader
import os, io, time
from cpos.esb.basic.application.app_ctrle_startpy import controlleeapp_start ,shellcall
from cpos.esb.basic.config import settings 
ctrl_reh_jrs = settings.CTRL_REH_JRS

esbapp_path = os.path.abspath( os.path.join(os.path.split(__file__)[0], '..') )

GREP_USER = os.environ['USER']  # Linux 上uwsgi代码所在的用户


def get_process(name, filter, user=None):
    #@param:name:进程名
    #@param:user:系统用户名
    if user:###针对多用户的情况，增加用户的查询
        cmd = 'ps -ef|grep ' + name + '|grep ' + user
    else:
        cmd = 'ps -ef|grep ' + name
    #print ('检测进程启动与否：%s'%( cmd ))
    r = os.popen(cmd)
    s = io.StringIO(r.read())
    pid = None
    for l in s:
        if filter(l):
            return filter(l)


def esbapp(x):
    if esbapp_path in x:
        d = x.split()
        if d[2] == '1':
            return d[1]
        else:
            return d[2]


def start():
    print('启动 jrs.app')
    pid = get_process(os.path.join('jrs','app.py'), esbapp, user=GREP_USER)
    if pid:
        print('jrs.app 已经启动，不需要再次启动')
    else:
        jrs_path = os.path.abspath( os.path.join(esbapp_path, 'jrs', 'app.py') )
        controlleeapp_start("jrsapp","jrsapp",ctrl_reh_jrs['port'],ctrl_reh_jrs['interval'],jrs_path)
        print('jrs.app 启动完毕')

    print('启动 pm.app')
    pid = get_process(os.path.join('pm','app.py'), esbapp, user=GREP_USER)
    if pid:
        print('pm.app 已经启动，不需要再次启动')
    else:
        pm_path = os.path.abspath( os.path.join(esbapp_path, 'pm', 'app.py') )
        controlleeapp_start("pmapp","pmapp",ctrl_reh_jrs['port'],ctrl_reh_jrs['interval'],pm_path)
        print('pm.app 启动完毕')


def stop():
    print('为 jrs/pm 提供停止命令')
    pid = get_process(os.path.join('bootstrap','jrs_stop_app.py'), esbapp, user=GREP_USER)
    if pid:
        print('jrs/pm 正在关闭，不需要再次启动停止命令')
    else:
        cmd = "python34 %s/bootstrap/jrs_stop_app.py"%(esbapp_path)
        print('jrs/pm 开始关闭 %s'%cmd)
        shellcall(cmd)


def restart():
    stop()
    time.sleep(2)
    start()


# 判断uwsgi是否启动，没有启动则重启一次
#用hxkh用户登录服务器,执行以下命令crontab -e,在命令打开的vi中加入以下代码:
#*/2 * * * * /home/hxkh/src/backplat/crontab/runpy.sh ks.py isalive
# runpy.sh 应该有可执行权限
# 代码含义:每2分钟的时间间隔自动执行命令: ks.py isalive


if __name__ == '__main__':
    import sys

    n = sys.argv[-1]
    if n.lower() == 'start':
        start()
    elif n.lower() == 'stop':
        stop()
    elif n.lower() == 'restart':
        restart()
    else:
        print('不支持该命令：', n)
