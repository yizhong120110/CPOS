# -*- coding: utf-8 -*-
"""
    核心日志、交易日志文件生成相关的配置
"""
import os
userhome = os.environ.get('HOME','')

# 核心日志生成目录
APPLOGPATH = "%s/log/syslog"%(userhome)

# 交易日志生成目录，主要是动态加载的代码中使用
DYLOGPATH = "%s/log/translog"%(userhome)

# 调试模式时会打印日志内容到控制台
LOG_ENABLE_CONSOLE = False
# 日志的过滤、显示级别
LOG_FILTER = ['FOUNDATION.TCP','FOUNDATION.AMQP']
LOG_LEVEL = "info"
LOG_LEVEL_TRANS = "info"
# print内容的输出文件
PRINTFILEPATH = "%s/log/print.log"%(userhome)

# 连接mongodb时使用的配置
MONGODB_IPS = ['46.17.167.220:5625']
LOG_MAP_DIC = {
    "translog":{"local_file":DYLOGPATH ,'dbname':"zhtsyw", 'collection':"translog"} ,
    "syslog"  :{"local_file":APPLOGPATH ,'dbname':"esbapp", 'collection':"syslog"}
    }

