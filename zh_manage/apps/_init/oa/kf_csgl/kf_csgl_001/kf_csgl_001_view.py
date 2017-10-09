# -*- coding: utf-8 -*-
# Action: 系统参数管理
# Author: jind
# AddTime: 2015-01-21
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, redirect,render_to_string,logger
from .kf_csgl_001_service import data_service,data_add_service,data_del_service,data_edit_service

@register_url('GET')
def index_view():
    """
    # 系统参数列表访问url
    """
    pt = request.GET.pt
    data = { 'pt': pt }
    return render_to_string( "kf_csgl/kf_csgl_001/kf_csgl_001.html", data )
    
@register_url('GET')
def data_view():
    """
    # 获取参数管理列表数据
    """
    # 获取rownum的开始和结束
    rn_start = request.rn_start
    rn_end = request.rn_end
    # 条件查询 条件名称
    search_name = request.GET.search_name
    # 条件查询 条件值
    search_value = request.GET.search_value
    data = {'total':0, 'rows':[]}
    try:
        data = data_service( search_name,search_value,rn_start,rn_end )
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('POST')
def data_add_view():
    """
    # 新增系统参数
    """
    # 平台
    pt = request.forms.pt
    # 参数代码
    csdm = request.forms.csdm
    # 参数值
    csz = request.forms.csz
    # 参数描述
    csms = request.forms.csms
    # 参数状态
    cszt = request.forms.cszt
    # 类型 1 -- 系统参数
    lx = '1' 
    result = {'state':False, 'msg':''}
    try:
        result = data_add_service( csdm,csz,csms,cszt,lx,pt )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    return result
    
@register_url('POST')
def data_edit_view():
    """
    # 编辑系统参数
    """
    # 平台
    pt = request.forms.pt
    # 参数ID
    csid = request.forms.csid
    # 参数值
    csz = request.forms.csz
    # 参数描述
    csms = request.forms.csms
    # 参数状态
    cszt = request.forms.cszt
    result = {'state':False, 'msg':''}
    try:
        result = data_edit_service( csid,csz,csms,cszt, pt )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    return result

@register_url('POST')
def data_del_view():
    """
    # 删除系统参数
    """
    # 平台
    pt = request.forms.pt
    # 删除参数id列表
    id_lst = request.forms.csids.split(',')
    result = {'state':False, 'msg':''}
    try:
        result = data_del_service( id_lst, pt )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    return result
