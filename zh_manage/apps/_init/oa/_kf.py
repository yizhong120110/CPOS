# -*- coding: utf-8 -*-
from bottle import request
from cpos3.conf import settings
from cpos3.bottleext.mako import render_to_string
from sjzhtspj import get_sess


_ROUTE_CFG = { 'method' : 'GET' }
@register_app(__file__)
def view():
    """
    开发系统主页访问url
    """
    # 从session中获取登录系统
    dlxt = get_sess("dlxt")
    # 获取行员信息
    hyobj = get_session_hyobj()
    return render_to_string("index.html", {'hyobj': hyobj,'dlxt':dlxt})
