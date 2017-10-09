# -*- coding: utf-8 -*-
"""
    url的通用处理部分
"""
import os, sys
from sjzhtspj import route, static_file, error, hook, request, redirect
from sjzhtspj import STATIC_DIR ,TMPDIR
from sjzhtspj import get_sess_hydm, check_sess, set_sess
from sjzhtspj import BaseRequest
from sjzhtspj import logger


# 通用错误的友好化处理
# 先注册的会被后注册的同code函数覆盖，这样可以不修改这个函数，然后在app中自行实现
@error(500)
def error500(error):
    print("500 error message:\n",error[-1],"\n=============================")
    return '500 error, nothing here, sorry!'


# url调用前的处理，可用于检查session
# 先注册的会被后注册的同名函数覆盖，这样可以不修改这个函数，然后在app中自行实现
@hook('before_request')
def before_request():
    # 这个判断是为了排除掉静态文件的控制
    # 对于登录的submit应该特殊处理，不使用request.method 
    special_url = ['/oa_core/choice', '/oa_core/login', '/oa_core/login_submit', '/sso/login', '/sso/hello' ]
#    if request.path != '/oa_core/choice' and request.path != '/oa_core/login' and request.path != '/oa_core/login_submit' and '.' not in request.path.split('/')[-1] :
    if request.path not in special_url and '.' not in request.path.split('/')[-1]:
        #print(request.environ['session'])
        # 只有未登录时需要下面，登录后不再跳转
        if get_sess_hydm() is None:
            if (request.is_ajax):
                # 如果是Ajax请求
                redirect('/oa_core/choice', 200)
            else:
                # 否则直接跳转到登陆
                redirect("/oa_core/choice")
        else:
            # 登录后每次请求需要检查是否被替代登录了，如果是，则退出
            if check_sess() == False:
                # 控制单一登录
                logger.warning("用户[%s]已在其他地方登录，本地退出"%(get_sess_hydm()))
                set_sess('hydm',None)
                redirect("/oa_core/choice")
    BaseRequest.MEMFILE_MAX = 1024 * 1024 * 20
    # 计算rownum的开始和结束，并赋值给request
    page = request.params.page or '1'
    rows = request.params.rows or '10'
    if page.isdigit() and rows.isdigit():
        request.rn_start = (int(page) - 1) * int(rows) + 1
        request.rn_end = request.rn_start + int(rows) - 1


# 是对static的文件通用处理
@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=STATIC_DIR)


# 是对tmp的文件通用处理
@route('/tmp/<filepath:path>')
def server_tmp(filepath):
    return static_file(filepath, root=TMPDIR)

