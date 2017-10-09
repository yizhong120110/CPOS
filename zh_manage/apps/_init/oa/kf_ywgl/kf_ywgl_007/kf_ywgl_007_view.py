# -*- coding: utf-8 -*-
# Action: 子流程列表
# Author: jind
# AddTime: 2015-01-06
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, redirect,render_to_string,logger
from .kf_ywgl_007_service import index_service,data_service,data_add_service,data_del_service

@register_url('GET')
def index_view():
    """
    # 子流程列表访问url
    """
    ywid = request.GET.ywid
    data = {'ywmc':[],'ywid':''}
    try:
        ywmc = index_service( ywid )
        data['ywmc'] = ywmc
        data['ywid'] = ywid
    except:
        logger.info(traceback.format_exc())
    return render_to_string( "kf_ywgl/kf_ywgl_007/kf_ywgl_007.html",data )
    
@register_url('GET')
def data_view():
    """
    # 获取子流程列表数据
    """
    #业务ID
    ywid = request.GET.ywid
    # 获取rownum的开始和结束
    rn_start = request.rn_start
    rn_end = request.rn_end
    data = {'total':0, 'rows':[]}
    try:
        data = data_service( ywid,rn_start,rn_end )
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('POST')
def data_add_view():
    """
    # 新增子流程
    """
    # 所属业务
    ssyw = request.forms.ssyw
    # 子流程名称
    zlcmc = request.forms.zlcmc
    # 子流程编码
    zlcbm = request.forms.zlcbm
    # 子流程描述
    zlcms = request.forms.zlcms
    # 类别 2:普通子流程
    lb = '2'
    result = {'state':False, 'msg':''}
    try:
        result = data_add_service( ssyw,zlcmc,zlcbm,zlcms,lb)
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    return result

@register_url('POST')
def data_del_view():
    """
    # 删除子流程
    """
    # 子流程ID
    zlcids_lst = request.forms.zlcids.split(',')
    result = {'state':False, 'msg':''}
    try:
        result = data_del_service( zlcids_lst )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    return result
