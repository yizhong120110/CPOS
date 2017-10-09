# -*- coding: utf-8 -*-
# Action: 节点管理
# Author: qish
# AddTime: 2015-01-10
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger
from sjzhtspj.common import jd_del_service
from .kf_jdgl_001_service import data_service, yycs_data_service


@register_url('GET')
def index_view():
    """
    # 节点管理列表访问url
    """
    return render_to_string("kf_jdgl/kf_jdgl_001/kf_jdgl_001.html")

@register_url('GET')
def data_view():
    """
    # 节点管理json数据
    """
    # 查询字段
    search_name = request.GET.search_name
    # 查询字段值
    search_value = request.GET.search_value
    params = {'search_name': search_name, 'search_value': search_value, 'rn_start': request.rn_start, 'rn_end': request.rn_end}
    
    data = {'total':0, 'rows':[]}
    try:
        data = data_service(params)
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('POST')
def data_del_view():
    """
    # 节点删除
    """
    # 节点ID，逗号分隔
    jdids = request.POST.jdids
    
    result = {'state':False, 'msg':''}
    try:
        result = jd_del_service(jdids)
    except:
        logger.info(traceback.format_exc())
    return result

@register_url('GET')
def yycs_index_view():
    """
    # 引用次数访问url
    """
    # 节点ID
    jdid = request.GET.jdid
    data = {'jdid': jdid}
    return render_to_string("kf_jdgl/kf_jdgl_001/kf_jdgl_001_yycs.html", data)

@register_url('GET')
def yycs_data_view():
    """
    # 引用次数信息查询
    """
    # 节点ID
    jdid = request.GET.jdid
    params = {'jdid': jdid}
    
    data = {'total':0, 'rows':[]}
    try:
        data = yycs_data_service(params)
    except:
        logger.info(traceback.format_exc())
    
    return data
