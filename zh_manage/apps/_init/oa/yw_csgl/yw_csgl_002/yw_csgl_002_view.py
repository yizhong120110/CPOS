# -*- coding: utf-8 -*-
# Action: 运维参数管理-业务参数
# Author: zhangchl
# AddTime: 2015-04-07
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string
from .yw_csgl_002_service import data_service


@register_url('GET')
def ywcsgl_indx_view():
    """
    # 业务参数管理主页面
    """
    pt = request.GET.pt
    data = { 'pt': pt }
    # 无需操作，直接到页面
    return render_to_string("yw_csgl/yw_csgl_002/yw_csgl_002.html",data)

@register_url('GET')
def data_view():
    """
    # 业务参数管理列表json数据
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    
    try:
        # 组织查询信息
        # 翻页开始下标
        rn_start = request.rn_start
        # 翻页结束下标
        rn_end = request.rn_end
        # 查询字段名称
        search_name = request.GET.search_name
        # 查询内容
        search_value = request.GET.search_value
        # 请求字典
        sql_data = { 'rn_start': rn_start, 'rn_end': rn_end }
        if search_value:
            sql_data.update( { 'search_name': [search_name], 'search_value': search_value } )
        # 调用service
        data = data_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    
    # 将结果反馈给前台
    return data