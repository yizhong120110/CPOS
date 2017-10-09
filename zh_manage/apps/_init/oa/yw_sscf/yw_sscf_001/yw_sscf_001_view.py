# -*- coding: utf-8 -*-
# Action: 大屏监控-大屏监控展示配置
# Author: zhangchl
# AddTime: 2015-05-28
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string
from .yw_sscf_001_service import (index_service,sxpl_edit_service,
                                server_add_sel_service,server_add_service,
                                page_reload_sjkhhs_service,page_reload_ywjymx_service,page_reload_jybs_service,page_reload_zjxx_service)

@register_url('GET')
def index_view():
    """
    # 大屏监控 主页面 view
    """
    # 初始化反馈前台信息
    data = { 'zjxx_lst': [], 'sxpl': '60' }
    try:
        # 调用数据库操作函数
        data = index_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 转到监控配置列表页面
    return render_to_string( "yw_sscf/yw_sscf_001/yw_sscf_001.html", data )

#@register_url('POST')
#def page_reload_view():
#    """
#    # 获取页面刷新数据
#    """
#    # 初始化反馈前台信息
#    data = { 'state': False, 'msg': '', 'zjxx_lst': [], 'jybs_dic': {}, 'ywjymx_lst': [], 'sjkhhs_dic': {} }
#    try:
#        # 调用数据库操作函数
#        data = page_reload_service()
#    except:
#        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
#        error_msg = traceback.format_exc()
#        logger.info(error_msg)
#        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
#    
#    # 将查询结果反馈给前台
#    return data
   
@register_url('POST')
def page_reload_sjkhhs_view():
    """
    # 获取数据库会话数数据
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'sjkhhs_lst': [] }
    try:
        # 调用数据库操作函数
        data = page_reload_sjkhhs_service()
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data
    
@register_url('POST')
def page_reload_ywjymx_view():
    """
    # 获取业务交易明细数据
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'ywjymx_lst': [] }
    try:
        # 调用数据库操作函数
        data = page_reload_ywjymx_service()
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data
    
@register_url('POST')
def page_reload_jybs_view():
    """
    # 获取交易笔数数据
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'jybs_dic': {} }
    try:
        # 调用数据库操作函数
        data = page_reload_jybs_service()
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data
    
@register_url('POST')
def page_reload_zjxx_view():
    """
    # 获取主机信息数据
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'zjxx_lst': []}
    try:
        # 调用数据库操作函数
        data = page_reload_zjxx_service()
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '页面初始化获取数据失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data

@register_url('POST')
def sxpl_edit_view():
    """
    # 编辑页面刷新频率
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '' }
    try:
        # 刷新频率
        sxpl = request.POST.sxpl
        # 原刷新评论
        ysxpl = request.POST.ysxpl
        # 调用数据库操作函数
        data = sxpl_edit_service( {'sxpl':sxpl, 'ysxpl': ysxpl} )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '更新页面刷新频率失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data

@register_url('POST')
def server_add_sel_view():
    """
    # 主机新增 页面初始化 获取数据 view
    """
    # 初始化反馈前台信息
    data = { 'zjxx_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 'state': False, 'msg': '' }
    try:
        # 调用数据库操作函数
        data = server_add_sel_service()
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取初始化新增页面数据失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data

@register_url('POST')
def server_add_view():
    """
    # 服务器新增提交 view
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '' }
    try:
        # 服务器名称
        servermc = request.POST.servermc
        # 服务器IP
        serverip = request.POST.serverip
        # 服务器类型(通讯、数据库、业务……)
        zjlx = request.POST.zjlx
        # 调用数据库操作函数
        data = server_add_service( {'mc':servermc, 'ip': serverip, 'zjlx': zjlx} )
    except:
        # 程序出现异常：将错误信息写到日志中，再将错误信息展示到前台
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    # 将查询结果反馈给前台
    return data