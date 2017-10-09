# -*- coding: utf-8 -*-
# Action: 行员日常运维流水展示
# Author: kongdq
# AddTime: 2015-04-29
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string
from .yw_hycz_001_service import index_service, data_service


@register_url('GET')
def index_view():
    """
    # 操作流水页面
    """
    # 初始化反馈前台信息
    data = { 'czpt_lst': [] }
    try:
        # 获取下拉列表信息
        data = index_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    
    return render_to_string("yw_hycz/yw_hycz_001/yw_hycz_001.html",data)

@register_url('GET')
def data_view():
    """
    # 操作流水json数据
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
        czsj = request.GET.czsj
        xm = request.GET.xm
        czpt = request.GET.czpt
        # 请求字典
        sql_data = { 'rn_start': rn_start, 'rn_end': rn_end,'czsj':czsj,'xm':xm,'czpt':czpt }
        # 调用service
        data = data_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    
    # 将结果反馈给前台
    return data
