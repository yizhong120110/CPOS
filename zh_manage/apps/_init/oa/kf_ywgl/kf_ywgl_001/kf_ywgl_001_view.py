# -*- coding: utf-8 -*-
# Action: 业务管理列表
# Author: gaorj
# AddTime: 2014-12-25
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger
from sjzhtspj.common import get_sjktbxx
from .kf_ywgl_001_service import data_service, data_add_service, data_del_service


@register_url('GET')
def index_view():
    """
    # 业务管理列表访问url
    """
    return render_to_string("kf_ywgl/kf_ywgl_001/kf_ywgl_001.html")

@register_url('GET')
def data_view():
    """
    # 业务管理列表json数据
    """
    data = {'total':0, 'rows':[]}
    
    try:
        data = data_service(request.rn_start, request.rn_end)
    except:
        logger.info(traceback.format_exc())
    
    return data

@register_url('POST')
def data_add_view():
    """
    # 业务新增
    """
    # 业务编码
    ywbm = request.forms.ywbm
    # 业务名称
    ywmc = request.forms.ywmc
    # 业务描述
    ywms = request.forms.ywms
    params = {'ywbm': ywbm, 'ywmc': ywmc, 'ywms': ywms}
    
    result = {'state':False, 'msg':''}
    
    try:
        result = data_add_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_del_view():
    """
    # 业务删除
    """
    ywids = request.POST.ywids
    params = {'ywids': ywids}
    
    result = {'state':False, 'msg':''}
    
    try:
        result = data_del_service(params)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_before_export_view():
    """
    # 业务管理导出前校验及数据获取
    """
    ywid = request.forms.ywid
    data = {'state':False, 'msg':'', 'sfywtj':False}
    
    try:
        # 校验业务下的数据库是否已同步
        sjktbxx_dic = get_sjktbxx( ywid )
        # 是否需要同步
        if sjktbxx_dic['sfxytb']:
            data['msg'] = '本地数据库未同步,请先执行同步操作'
            return data
        data['state'] = True
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '数据库数据交易出现异常！异常错误提示信息[%s]' % error_msg
    
    return data
