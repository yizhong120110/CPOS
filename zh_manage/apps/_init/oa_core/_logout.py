# -*- coding: utf-8 -*-
from sjzhtspj import request, redirect
from sjzhtspj import set_sess


_ROUTE_CFG = {'method': 'GET'}
@register_app(__file__)
def view():
    """
    注销
    """
    set_sess('hydm',None)
    return redirect("/")
