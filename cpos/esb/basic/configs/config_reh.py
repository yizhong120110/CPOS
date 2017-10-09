# -*- coding: utf-8 -*-
"""
 controller and controllee
"""
# jrs进程
CTRL_REH_JRS  = {'port':5611, 'interval': 10 }

# RDC
CTRL_RDCS = {
    # 固定只启动1个
    'count':1 ,
    "port":5612 ,
    'interval':5 ,
    "max_waittime":10 ,
    }

# JR 由JRS来启动，数量的变化后需求重启jrs
CTRL_RE_JR = {
    "init_config":{
                    'jy':{'count':1,'interval':10},
                    'fx':{'count':1,'interval':10},
                    'cj':{'count':1,'interval':10},
                    'dz':{'count':1,'interval':10},
                    'qt':{'count':1,'interval':10},
                    'cz':{'count':1,'interval':10},
                  },
    "port":5613,
    }

# 系统相关的进程，这里只是一个挡板，运行后应该由数据库提供
import os
# 当前文件目录是cpos\esb\basic\configs
# apppath的文件目录是 cpos\esb\app
apppath = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..', '..', 'app'))
CTRL_RE_PM = {
    "init_config":{
        # 这些是系统配置的，其他的需要在数据库中增加类别
        'tp':          {'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'tp','app.py'))},
        'rpclp':       {'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'lp','app.py')) ,'apparg':'rpclog'},
        'filelp':      {'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'lp','app.py'))},
        'js':          {'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'js','app.py'))},
        'rdcs':        {'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'rdcs','app.py'))},
        'icm':         {'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'icm','app.py'))},
        'ocm_file_get':{'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'ocm','app.py')) ,'apparg':'ocm_file_get'},
        'ocm_file_put':{'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'ocm','app.py')) ,'apparg':'ocm_file_put'},
        'ftp_file_get':{'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'ocm','app.py')) ,'apparg':'ftp_file_get'},
        'ftp_file_put':{'count':1 ,'appfilepath':'%s'%(os.path.join(apppath,'ocm','app.py')) ,'apparg':'ftp_file_put'},
#        # ocm_short_tcp 应该由db提供配置路径
#        'ocm_short_tcp':{'count':1,'appfilepath':'%s'%(os.path.join(apppath ,'..','..','ops','ocm','ocm_short_tcp.py')) ,'apparg':'ocm_short_tcp'},
#        'icp':         {'count':5 ,'appfilepath':'%s'%(os.path.join(apppath,'icp','app.py')),'apparg':'icpserv_fwdtest.py'}, 
                  },
     "port":5614, "interval":10,
    }


