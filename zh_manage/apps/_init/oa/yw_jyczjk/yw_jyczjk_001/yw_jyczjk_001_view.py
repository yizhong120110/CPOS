# -*- coding: utf-8 -*-
# Action: 冲正监控
# Author: zhangchl
# AddTime: 2015-10-29
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, json, os
from sjzhtspj import logger, request, render_to_string, TMPDIR, response
from sjzhtspj.common import get_strftime2
from .yw_jyczjk_001_service import ( index_service, data_service, select_log_service, 
                                    czjyrz_ck_service, sgcz_service )

@register_url('GET')
def index_view():
    """
    # 冲正监控 主页面
    """
    # 平台
    pt = request.GET.pt
    # 初始化反馈前台信息
    data = { 'zt_lst': [], 'pt': pt, 'nowdate': '' }
    try:
        # 组织请求信息字典
        sql_data = { 'pt': pt }
        # 调用数据库操作函数
        data = index_service( sql_data )
        # 将对应平台反馈给前台
        data['pt'] = pt
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 转到交易监控列表页面
    return render_to_string( "yw_jyczjk/yw_jyczjk_001/yw_jyczjk_001.html", data )

@register_url('POST')
def data_view():
    """
    # 自动发起交易列表json数据 view
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 平台
        pt = request.POST.pt
        # 交易日期
        jyrq = request.POST.jyrq
        jyrq = jyrq.replace('-','')
        # 交易流水号
        ylsh = request.POST.ylsh
        # 冲正流水号
        czlsh = request.POST.czlsh
        # 冲正流水状态
        czlshzt = request.POST.czlshzt
        # 交易名称
        jymc = request.POST.jymc
        # 交易码
        jym = request.POST.jym
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'pt': pt, 'jyrq': jyrq, 'ylsh': ylsh, 'czlsh': czlsh, 'czlshzt': czlshzt,
                    'jymc': jymc, 'jym': jym, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def select_log_view():
    """
    # 查看流程日志
    """
    # 初始化反馈信息
    # rznr： 日志内容
    result = { 'state':False, 'msg': '', 'rznr':'' }
    try:
        # 交易日期
        jyrq = request.POST.jyrq
        # 流水号
        lsh = request.POST.lsh
        # 组织查询字典
        sql_data = { 'jyrq': jyrq, 'lsh': lsh }
        result = select_log_service( sql_data )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '获取日志失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def czjyrz_ck_view():
    """
    # 冲正交易执行子流程步骤列表
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 交易日期
        jyrq = request.POST.jyrq
        # 交易流水号
        lsh = request.POST.lsh
        # 组织调用函数字典
        data_dic = { 'jyrq': jyrq, 'lsh': lsh }
        # 调用操作数据库函数
        data = czjyrz_ck_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    
    # 将组织的结果反馈给前台
    return data

@register_url('POST')
def sgcz_view():
    """
    # 手工冲正
    """
    # 初始化反馈信息
    # rznr： 日志内容
    result = { 'state':False, 'msg': '发起失败' }
    try:
        # 交易日期
        jyrq = request.POST.jyrq
        # 流水号
        lsh = request.POST.lsh
        # 冲正流水号
        czlsh = request.POST.czlsh
        # 组织查询字典
        sql_data = { 'jyrq': jyrq, 'ylsh': lsh, 'czlsh': czlsh if czlsh !='null' else '' }
        result = sgcz_service( sql_data )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '手工冲正出现失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
    
    
    
    
    
    
    
    
    