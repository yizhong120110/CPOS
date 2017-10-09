# -*- coding: utf-8 -*-
# Action: 公共函数view
# Author: zhangzf
# AddTime: 2015-1-6
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, logger, render_to_string
from .kf_ywgl_017_service import data_service, add_service, del_service, update_service

@register_url('GET')
def index_view():
    """
    # 公共函数url
    """
    ywid = request.GET.ywid
    
    data = {'ywid': ywid}
    return render_to_string("kf_ywgl/kf_ywgl_017/kf_ywgl_017.html", data)

@register_url('GET')
def data_view():
    """
    # 查询所有公共函数
    """
    
    # 业务ID
    ywid = request.GET.ywid
    # 函数名称
    hsmc = request.GET.hsmc
    # 函数描述
    hsms = request.GET.hsms
    # 计算rownum的开始和结束
    rn_start = request.rn_start
    rn_end = request.rn_end    
    result = {'total':0, 'rows':[]}
    try:
        # 查询所有公共函数
        result = data_service({'ywid':ywid,'hsmc':hsmc,'hsms':hsms, 'rn_start':rn_start, 'rn_end':rn_end})
    except:
        logger.info(traceback.format_exc())
    return result
        
@register_url('POST')
def add_view():
    """
    # 添加公共函数
    """
    
    # 函数名称
    mc = request.forms.mc
    # 函数描述
    hsms = request.forms.hsms
    # 函数内容
    hsnr = request.forms.hsnr
    # 业务id
    ywid = request.forms.ywid
    
    result = {'state': False, 'msg':''}
    try:
        # 添加公共函数
        result = add_service({'mc':mc, 'hsms':hsms, 'hsnr':hsnr, 'ywid':ywid})
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def del_view():
    """
    # 删除公共函数
    """
    # BLOB管理表id
    nrids = request.forms.nrids
    # 公共函数表id
    ids = request.forms.ids
    # 业务id
    ywid = request.forms.ywid
    
    result = {'state': False, 'msg':''}
    try:
        # 删除公共函数
        result = del_service({'nrids':nrids, 'ids':ids, 'ywid':ywid})
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result
    
@register_url('POST')
def update_view():
    """
    # 更新公共函数
    """
    # 函数内容id
    nr_id = request.forms.nr_id
    # 公共函数id
    id = request.forms.id
    # 函数名称
    mc = request.forms.mc
    # 函数描述
    hsms = request.forms.hsms
    # 函数内容
    nr = request.forms.hsnr
    # 业务id
    ywid = request.forms.ywid
    
    result = {'state': False, 'msg':''}
    try:
        # 更新公共函数
        result = update_service({'nr_id':nr_id, 'id':id, 'mc':mc, 'hsms':hsms, 'nr':nr, 'ywid':ywid})
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    
    return result
