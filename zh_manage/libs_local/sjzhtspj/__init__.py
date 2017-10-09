# -*- coding: utf-8 -*-

import os
from bottle import run, default_app
from bottle import redirect, route, static_file, error, hook
from bottle import request
from bottle import response
from bottle import BaseRequest

# 项目的根目录、apps目录、static目录
from path_init import ROOT_DIR, APPS_DIR, STATIC_DIR, MODELSQL_DIR


# ################ 成组出现的时候，python start.py 才会写log ################
from cpos3.conf import settings

settings.register_yaml(os.path.join(ROOT_DIR, 'etc', 'main.yaml'))
from cpos3.utils.log import log as app_log

logger = app_log.log
# log的写法
logger.info('=====locallib running(logger start)=====')
# ################################################################################


# session相关内容
from .session import get_SessionApp
sess_app = get_SessionApp(default_app(), settings.LOGDIR)
from .session import set_sess, get_sess_hydm,get_sess, set_userid, check_userid
sess_id_cache = None
if settings.SESS_ID_ONLY == True:
    import redis
    sess_id_cache = redis.StrictRedis(**settings.SESS_ID_CONSTR)
def set_sess_uuid():
    return set_userid(sess_id_cache)
def check_sess():
    return check_userid(sess_id_cache)

# 文件的编码检查
from cpos3.utils.charset import get_err_codingfile

# ################################################################################
# mako模板文件目录
settings.TEMPLATE_DIRS = [
    APPS_DIR,
]
# ################################################################################

# web开发的常用函数
from cpos3.bottleext.mako import render_to_string
from cpos3.bottleext.mako import render_string
from cpos3.utils.ftools import register


# modelsql对象
from .modelsql import init_models_sql
ModSql = init_models_sql()

import cpos3.utils.apis

# 存放临时文件,可以定期清理
TMPDIR = settings.TMPDIR
# 存放通讯客户端文件：ocm
OCMDIR = settings.OCMDIR
# 存放通讯服务端文件：icp
ICPDIR = settings.ICPDIR

#from cpos3.utils.ftools import AttrDict
#settings._T = AttrDict({"APP_NAME":"_init"})
