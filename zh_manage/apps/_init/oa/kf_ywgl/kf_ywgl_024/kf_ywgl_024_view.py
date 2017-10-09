# -*- coding: utf-8 -*-
# Action: 交易列表View
# Author: zhangzf
# AddTime: 2015-1-4
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, logger, render_to_string
from .kf_ywgl_024_service import index_service, data_service, add_service, del_service, jyzt_upd_service

@register_url('GET')
def index_view():
    """
    # 交易列表url
    """
    ywid = request.GET.ywid
    data = {}
    try:
        # 获取业务列表
        data = index_service(ywid)
    except:
        logger.info(traceback.format_exc())    
    return render_to_string("kf_ywgl/kf_ywgl_024/kf_ywgl_024.html", data)

@register_url('post')
def data_view():
    """
    # 交易列表查询
    """
    
    # 业务ID
    ywid = request.GET.ywid
    # 条件查询 条件名称
    search_name = request.GET.search_name
    # 条件查询 条件值
    search_value = request.GET.search_value
    # rownum的开始和结束
    rn_start = request.rn_start
    rn_end = request.rn_end
    # 返回对象
    result = {}
    try:
        result = data_service(ywid, search_name, search_value, rn_start, rn_end)
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '获取信息失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def add_view():
    """
    # 添加交易
    """
    
    # 所属业务
    ssywid = request.forms.ssywid
    # 交易名称
    jymc = request.forms.jymc
    # 交易码
    jym = request.forms.jym
    # 交易描述
    jyms = request.forms.jyms
    # 交易状态
    jyzt = '1' if request.forms.jyzt == 'on' else '0'
    # 返回对象
    result = {'state':False, 'msg':''}
    try:
        result = add_service(ssywid, jymc, jym, jyms, jyzt)
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def del_view():
    """
    # 删除交易
    """
    
    ids_lst = request.forms.ids.split(',')
    result = {'state':False, 'msg':''}
    try:
        result = del_service(ids_lst)
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    return result

@register_url('POST')
def jyzt_upd_view():
    """
    # 批量设置交易状态
    """
    result = {'state':False, 'msg':''}
    try:
        # 操作交易id
        ids_lst = request.forms.ids.split(',')
        # 操作类型: qy(启用):0， jy（禁用）:1
        cztype = request.forms.cztype
        data_dic = { 'ids_lst': ids_lst, 'cztype': cztype }
        print ( data_dic )
        result = jyzt_upd_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '批量修改交易状态失败！异常错误提示信息[%s]' % error_msg
    return result
    
    
    
    