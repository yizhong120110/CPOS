# -*- coding: utf-8 -*-

from bottle import request
from beaker.middleware import SessionMiddleware
import base64, os

# 这是用于浏览器、服务器交互session使用的值
# 也可以使用不固定的，更易防止爬虫
env_sess_key = 'session'

def get_SessionApp(app, session_data_dir):
    session_opts = {
        'session.type': 'file',
        # cookie_expires 单位是秒，True可以一直不断开，直到浏览器关闭
        'session.cookie_expires': True,
        # timeout 服务端的session有效时间，指自无操作开始计算
        'session.timeout': 3600,
        'session.data_dir': session_data_dir,
        'session.auto': True,
    }
    return SessionMiddleware(app, session_opts, environ_key=env_sess_key)

def set_sess(key,value):
    """
    # session赋值
    :param key: 关键字
    :param value: 值
    :return:
    """
    if not request.environ[env_sess_key].get(key):
        request.environ[env_sess_key][key] = None
    request.environ[env_sess_key][key] = value
    return True

def get_sess(key):
    """
    # session 取值
    :param key: 关键字
    :return: value
    """
    try:
        return request.environ[env_sess_key].get(key,None)
    except:
        return None

def get_sess_hydm():
    """
    # 获取行员代码
    :return:
    """
    return get_sess("hydm")

def set_userid(sess_id_cache):
    """
    # 控制单一session登录
    """
    sess_id = base64.encodebytes(os.urandom(20))
    set_sess("sess_id",sess_id)
    # 将hydm+sess_id 的映射关系放到memcache中
    if sess_id_cache is not None:
        hydm = get_sess_hydm()
        if hydm is not None:
            sess_id_cache.set(hydm, sess_id)
    return True

def check_userid(sess_id_cache):
    """
    # 检查session中的值是否等同于memcache中的值
    """
    if sess_id_cache is None:
        return True
    sess_str = get_sess("sess_id")
    hydm = get_sess_hydm()
    memc_str = sess_id_cache.get(hydm)
    if sess_str is not None and sess_str == memc_str:
        return True
    return False
