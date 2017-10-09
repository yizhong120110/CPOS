# -*- coding: utf-8 -*-
# Action: 导入历史 view
# Author: zhangchl
# AddTime: 2015-01-12
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request,render_to_string
from .yw_ywsj_001_service import data_service, data_edit_sel_service, data_edit_service, get_yw_tx_service

@register_url('GET')
def index_view():
    """
    # 导入历史url
    """
    # 组织反馈信息
    return render_to_string( "yw_ywsj/yw_ywsj_001/yw_ywsj_001.html")

@register_url('GET')
def data_view():
    """
    # 导入历史：获取显示数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 查询条件key
        search_name = request.GET.search_name
        # 查询条件value
        search_value = request.GET.search_value
        # 组织调用函数字典
        data_dic = { 'rn_start': rn_start, 'rn_end': rn_end,'search_name':search_name,'search_value':search_value }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        
    return data

@register_url('POST')
def data_edit_sel_view():
    """
    # 导入历史：信息编辑 页面初始化 view
    """
    # 反馈信息
    result = {'state': False, 'msg':'', 'drlsid':'', 'czms': '', 'bz': ''}
    try:
        # 导入id
        drlsid = request.forms.drlsid
        # 组织调用函数字典
        data_dic = { 'drlsid': drlsid }
        # 组织调用函数字典
        result = data_edit_sel_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '获取页面初始化数据出现错误！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_edit_view():
    """
    # 导入历史：信息编辑 提交 view 
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 导入流水id
        drlsid = request.forms.drlsid
        # 操作描述
        czms = request.forms.czms
        # 操作描述
        bz = request.forms.bz
        # 组织调用函数字典
        data_dic = { 'drlsid': drlsid, 'czms': czms, 'bz': bz }
        # 调用操作数据库函数
        result = data_edit_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def get_yw_tx_view():
    """
    # 获取业务或者通讯的view
    """
    # 反馈信息
    result = {'state': False, 'msg':''}
    try:
        # 内容类型
        lx = request.GET.lx
        # 是否是导入
        dr = request.GET.dr
        # 组织调用函数字典
        data_dic = { 'lx': lx, 'dr': dr}
        # 调用操作数据库函数
        result = get_yw_tx_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info( error_msg )
        result['msg'] = '获取列表失败！异常错误提示信息[%s]' % error_msg
    
    return result
