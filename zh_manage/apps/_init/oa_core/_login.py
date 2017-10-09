# -*- coding: utf-8 -*-
from bottle import request
from cpos3.conf import settings
from cpos3.bottleext.mako import render_to_string


_ROUTE_CFG = { 'method' : 'GET' }
@register_app(__file__)
def view():
    """
    主页访问url
    """
    return render_to_string("login-dev.html")
