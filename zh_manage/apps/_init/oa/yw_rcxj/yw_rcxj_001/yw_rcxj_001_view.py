# -*- coding: utf-8 -*-
# Action: 交易监控
# Author: zhangchl
# AddTime: 2015-04-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

# 处理程序异常模块
import traceback
# 引入日志模块，请求模块，反馈页面模块
from sjzhtspj import logger, render_to_string,request
# 引入本功能数据库操作函数
from .yw_rcxj_001_service import index_service, data_zjjk_service, data_sjkxj_service, data_jcxj_service, data_logxj_service,export_pdf_service,data_down_service,delDC_service

@register_url('GET')
def index_view():
    """
    # 日常巡检 主页面
    """
    # 初始化反馈前台信息
    data = { 'datetime': [] }
    try:
        # 调用数据库操作函数
        data = index_service( data )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 转到日常巡检主页面
    return render_to_string( "yw_rcxj/yw_rcxj_001/yw_rcxj_001.html", data )

@register_url('GET')
def data_zjxj_view():
    """
    # 主机巡检信息查询
    # 业务信息json数据
    """
    data = {'total':0, 'rows':[]}
    try:
        data = data_zjjk_service()
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('GET')
def data_sjkxj_view():
    """
    # Oracle数据库巡检信息查询
    # 业务信息json数据
    """
    data = {'total':0, 'rows':[]}
    try:
        data = data_sjkxj_service()
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('GET')
def data_jcxj_view():
    """
    # Oracle数据库巡检信息查询
    # 业务信息json数据
    """
    data = {'total':0, 'rows':[]}
    try:
        data = data_jcxj_service()
    except:
        logger.info(traceback.format_exc())
    return data
    
@register_url('GET')
def data_Tonglogxj_view():
    """
    # Oracle数据库巡检信息查询
    # 业务信息json数据
    """
    data = {'total':0, 'rows':[]}
    try:
        data = data_logxj_service()
    except:
        logger.info(traceback.format_exc())
    return data
    
@register_url('POST')
def export_pdf_view():
    """
    # pdf导出功能
    """
    data = {'state':False, 'msg':''}
    export_data = request.forms.export_data
    try:
        data = export_pdf_service(export_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '导出失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('GET')
def data_down_view():
    """
    # pdf下载功能
    """
    data = {'state':False, 'msg':''}
    filepath = request.GET.filepath
    try:
        data = data_down_service(filepath)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '下载失败！异常错误提示信息\n[%s]' % error_msg
    return data
    
@register_url('POST')
def delDC_view():
    """
    # 文件删除功能
    """
    data = {'state':False, 'msg':''}
    filepath = request.forms.filepath
    try:
        data = delDC_service(filepath)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    return data