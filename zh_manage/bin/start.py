# -*- coding: utf-8 -*-
"""
    程序开发模式的启动入口
    本脚本没有使用一个function将代码包起来的原因是，uwsgi启动时需要指定--file到该py
        单独测试时application = default_app()可以被调起，start()方式不行
        默认直接调用application，这里提供的是app，所以要参数--callable app
    if __name__ == "__main__" 是为了调试时使用，也可以加上else，作为uwsgi调用时使用的部分
"""
# path_init 是为了对PYTHONPATH做初始化
import path_init
import sys

from sjzhtspj import run, logger
from sjzhtspj import settings
from sjzhtspj import sess_app as app

logger.info('=====start.py running(debug)=====')

# apps_init中的内容依赖于settings，稍晚引用
from apps_init import apps_init
# 加载应用，创建应用下静态文件的软连接、脚本的URL
apps_init()
if __name__ == "__main__":
    args = sys.argv
    # 不止一个参数，满足ip:port的格式 ip格式非法未校验
    if len(args) > 1 and args[1].find(':') > -1:
        hostip, port = args[1].split(':')
    else:
        #从此处init_log，每个子程序使用log.info，不使用log对象传递
        hostip = '127.0.0.1'
        port = 13597
        # reloader=True 时，程序启动会连做两遍
    # debug和reloader 仅应应用于开发环境，不应应用于生产环境
    run(app=app, host=hostip, port=port, reloader=True, debug=settings.DEBUG)

