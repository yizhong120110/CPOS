# -*- coding: utf-8 -*-
# Action: 交易/子流程查看
# Author: gaorj
# AddTime: 2015-01-04
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, json
from sjzhtspj import request, render_to_string, logger
from sjzhtspj.common import xml_out, lc_data_service
from .kf_ywgl_004_service import index_service


@register_url('GET')
def index_view():
    """
    # 交易流程查看url
    """
    # 类型('lc'流程, 'zlc'子流程)
    lx = request.GET.lx
    # 交易/子流程ID
    id = request.GET.id
    params = {'lx': lx, 'id': id}
    
    data = {'lx': lx, 'id': id, 'mc': ''}
    try:
        data = index_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_ywgl/kf_ywgl_004/kf_ywgl_004.html", data)

@register_url('GET')
def data_view():
    """
    # 交易/子流程查看获取数据
    """
    # 交易/子流程ID
    id = request.GET.id
    # 类型('lc'交易, 'zlc'子流程)
    lx = request.GET.lx
    
    data = [{}, []]
    try:
        data = lc_data_service(id, lx)
    except:
        logger.info(traceback.format_exc())
    
    return json.dumps(data)

@register_url('GET')
def data_xml_view():
    """
    # 交易/子流程查看获取xml数据
    """
    # 交易/子流程ID
    id = request.GET.id
    # 类型('lc'交易, 'zlc'子流程)
    lx = request.GET.lx
    
    xml = 'Error'
    with sjapi.connection() as db:
        xml = xml_out(db, lx, id)
    return xml
