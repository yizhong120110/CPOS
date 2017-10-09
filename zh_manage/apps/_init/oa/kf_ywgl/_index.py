# -*- coding: utf-8 -*-
# Action: 交易参数获取
# Author: gaorj
# AddTime: 2014-12-25
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from bottle import request
from cpos3.conf import settings
from cpos3.bottleext.mako import render_to_string


_ROUTE_CFG = { 'method' : 'GET' }
@register_app(__file__)
def view():
    """
    #交易基本信息url
    """
    ywid = request.GET.ywid
    
    return render_to_string("kf_ywgl/kf_ywgl.html", {'ywid': ywid})
