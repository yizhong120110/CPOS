# -*- coding: utf-8 -*-
from sjzhtspj import redirect
from sjzhtspj import render_to_string
from sjzhtspj import get_sess


_ROUTE_CFG = {'method': 'GET'}


@register_app(__file__)
def view():
    """
    主页访问url，仅作占位，由各个app实现
    """
    #    return "这里是登录后的首页，欢迎光临"
    hyobj = get_session_hyobj()
    #dlxt = get_sess("dlxt")
    return render_to_string("index.html", {'hyobj': hyobj,"dlxt":dlxt})
