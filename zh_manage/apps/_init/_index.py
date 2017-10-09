# -*- coding: utf-8 -*-
from sjzhtspj import request, redirect, route
from sjzhtspj import settings
from sjzhtspj import render_to_string


_ROUTE_CFG = {'method': 'GET'}
@register_app(__file__)
def view():
    """
    主页访问url
    """
    return redirect("/oa/kf")
