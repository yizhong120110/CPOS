# -*- coding: utf-8 -*-
# Action: 运维监控配置列表
# Author: fangch
# AddTime: 2015-04-11
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string
from .yw_jhrw_002_service import data_service,data_ymxx_service,data_xydzlb_service

@register_url('GET')
def index_view():
    """
    # 运维监控配置列表页面
    """
    # 初始化反馈前台信息
    data = { 'zt_lst': [], 'gzlb_lst': [] }
    try:
        # 获取下拉列表信息
        data = data_ymxx_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 转到监控配置列表页面
    return render_to_string("yw_jhrw/yw_jhrw_002/yw_jhrw_002.html",data)

@register_url('POST')
def data_view():
    """
    # 监控规则发起列表信息json数据
    """
    data = {'total':0, 'rows':[]}
    # 规则类别
    gzlb = request.POST.gzlb
    # 配置名称
    pzmc = request.POST.pzmc
    # 分析规则或指标
    gzzb = request.POST.gzzb
    # 状态
    zt = request.POST.zt
    params = { 'rn_start': request.rn_start, 'rn_end': request.rn_end, 'gzlb':gzlb, 'pzmc':pzmc, 'fxgzzb':gzzb, 'zt':zt}
    try:
        data = data_service(params)
    except:
        logger.info(traceback.format_exc())
    return data
    
@register_url('POST')
def xydzlb_sel_view():
    """
    # 响应动作列表json数据
    """
    # 获取配置ID查询使用
    pzid = request.POST.pzid
    params = { 'pzid':pzid }
    # 定义反馈信息
    data = {'total':0, 'rows':[] }
    try:
        data = data_xydzlb_service(params)
    except:
        logger.info(traceback.format_exc())
    return data